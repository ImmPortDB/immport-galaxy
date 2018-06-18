import six
from social_core.actions import do_auth, do_complete, do_disconnect
from social_core.backends.utils import get_backend
from social_core.strategy import BaseStrategy
from social_core.utils import module_member, setting_name
from sqlalchemy.exc import IntegrityError

from ..authnz import IdentityProvider
from ..model import PSAAssociation, PSACode, PSANonce, PSAPartial, UserAuthnzToken


# key: a component name which PSA requests.
# value: is the name of a class associated with that key.
DEFAULTS = {
    'STRATEGY': 'Strategy',
    'STORAGE': 'Storage'
}

BACKENDS = {
    'google': 'social_core.backends.google_openidconnect.GoogleOpenIdConnect'
}

BACKENDS_NAME = {
    'google': 'google-openidconnect'
}

AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address.
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details'
)

DISCONNECT_PIPELINE = (
    'galaxy.authnz.psa_authnz.allowed_to_disconnect',
    'galaxy.authnz.psa_authnz.disconnect'
)


class PSAAuthnz(IdentityProvider):
    def __init__(self, provider, oidc_config, oidc_backend_config):
        self.config = {'provider': provider.lower()}
        for key, value in oidc_config.iteritems():
            self.config[setting_name(key)] = value

        self.config[setting_name('USER_MODEL')] = 'models.User'
        self.config['SOCIAL_AUTH_PIPELINE'] = AUTH_PIPELINE
        self.config['DISCONNECT_PIPELINE'] = DISCONNECT_PIPELINE
        self.config[setting_name('AUTHENTICATION_BACKENDS')] = (BACKENDS[provider],)

        # The following config sets PSA to call the `_login_user` function for
        # logging in a user. If this setting is set to false, the `_login_user`
        # would not be called, and as a result Galaxy would not know who is
        # the just logged-in user.
        self.config[setting_name('INACTIVE_USER_LOGIN')] = True

        if provider == 'google':
            self._setup_google_backend(oidc_backend_config)

    def _setup_google_backend(self, oidc_backend_config):
        self.config[setting_name('AUTH_EXTRA_ARGUMENTS')] = {'access_type': 'offline'}
        self.config['SOCIAL_AUTH_GOOGLE_OPENIDCONNECT_KEY'] = oidc_backend_config.get('client_id')
        self.config['SOCIAL_AUTH_GOOGLE_OPENIDCONNECT_SECRET'] = oidc_backend_config.get('client_secret')
        self.config['redirect_uri'] = oidc_backend_config.get('redirect_uri')
        if oidc_backend_config.get('prompt') is not None:
            self.config[setting_name('AUTH_EXTRA_ARGUMENTS')]['prompt'] = oidc_backend_config.get('prompt')

    def _on_the_fly_config(self, trans):
        trans.app.model.PSACode.trans = trans
        trans.app.model.UserAuthnzToken.trans = trans
        trans.app.model.PSANonce.trans = trans
        trans.app.model.PSAPartial.trans = trans
        trans.app.model.PSAAssociation.trans = trans

    def _get_helper(self, name, do_import=False):
        this_config = self.config.get(setting_name(name), DEFAULTS.get(name, None))
        return do_import and module_member(this_config) or this_config

    def _get_current_user(self, trans):
        return trans.user if trans.user is not None else None

    def _load_backend(self, strategy, redirect_uri):
        backends = self._get_helper('AUTHENTICATION_BACKENDS')
        backend = get_backend(backends, BACKENDS_NAME[self.config['provider']])
        return backend(strategy, redirect_uri)

    def _login_user(self, backend, user, social_user):
        self.config['user'] = user

    def authenticate(self, trans):
        self._on_the_fly_config(trans)
        strategy = Strategy(trans, Storage, self.config)
        backend = self._load_backend(strategy, self.config['redirect_uri'])
        return do_auth(backend)

    def callback(self, state_token, authz_code, trans, login_redirect_url):
        self._on_the_fly_config(trans)
        self.config[setting_name('LOGIN_REDIRECT_URL')] = login_redirect_url
        strategy = Strategy(trans, Storage, self.config)
        strategy.session_set(BACKENDS_NAME[self.config['provider']] + '_state', state_token)
        backend = self._load_backend(strategy, self.config['redirect_uri'])
        redirect_url = do_complete(
            backend,
            login=lambda backend, user, social_user: self._login_user(backend, user, social_user),
            user=self._get_current_user(trans),
            state=state_token)
        return redirect_url, self.config.get('user', None)

    def disconnect(self, provider, trans, disconnect_redirect_url=None, association_id=None):
        self._on_the_fly_config(trans)
        self.config[setting_name('DISCONNECT_REDIRECT_URL')] =\
            disconnect_redirect_url if disconnect_redirect_url is not None else ()
        strategy = Strategy(trans, Storage, self.config)
        backend = self._load_backend(strategy, self.config['redirect_uri'])
        response = do_disconnect(backend, self._get_current_user(trans), association_id)
        if isinstance(response, six.string_types):
            return True, "", response
        return response.get('success', False), response.get('message', ""), ""


class Strategy(BaseStrategy):

    def __init__(self, trans, storage, config, tpl=None):
        self.trans = trans
        self.request = trans.request
        self.session = trans.session if trans.session else {}
        self.config = config
        self.config['SOCIAL_AUTH_REDIRECT_IS_HTTPS'] = True if self.trans.request.host.startswith('https:') else False
        self.config['SOCIAL_AUTH_GOOGLE_OPENIDCONNECT_EXTRA_DATA'] = ['id_token']
        super(Strategy, self).__init__(storage, tpl)

    def get_setting(self, name):
        return self.config[name]

    def session_get(self, name, default=None):
        return self.session.get(name, default)

    def session_set(self, name, value):
        self.session[name] = value

    def session_pop(self, name):
        raise NotImplementedError('Not implemented.')

    def request_data(self, merge=True):
        if not self.request:
            return {}
        if merge:
            data = self.request.GET.copy()
            data.update(self.request.POST)
        elif self.request.method == 'POST':
            data = self.request.POST
        else:
            data = self.request.GET
        return data

    def request_host(self):
        if self.request:
            return self.request.host

    def build_absolute_uri(self, path=None):
        path = path or ''
        if path.startswith('http://') or path.startswith('https://'):
            return path
        return \
            self.trans.request.host +\
            '/authn' + ('/' + self.config.get('provider')) if self.config.get('provider', None) is not None else ''

    def redirect(self, url):
        return url

    def html(self, content):
        raise NotImplementedError('Not implemented.')

    def render_html(self, tpl=None, html=None, context=None):
        raise NotImplementedError('Not implemented.')

    def start(self):
        self.clean_partial_pipeline()
        if self.backend.uses_redirect():
            return self.redirect(self.backend.auth_url())
        else:
            return self.html(self.backend.auth_html())

    def complete(self, *args, **kwargs):
        return self.backend.auth_complete(*args, **kwargs)

    def continue_pipeline(self, *args, **kwargs):
        return self.backend.continue_pipeline(*args, **kwargs)


class Storage:
    user = UserAuthnzToken
    nonce = PSANonce
    association = PSAAssociation
    code = PSACode
    partial = PSAPartial

    @classmethod
    def is_integrity_error(cls, exception):
        return exception.__class__ is IntegrityError


def allowed_to_disconnect(name=None, user=None, user_storage=None, strategy=None,
                          backend=None, request=None, details=None, **kwargs):
    """
    Disconnect is the process of disassociating a Galaxy user and a third-party authnz.
    In other words, it is the process of removing any access and/or ID tokens of a user.
    This function should raise an exception if disconnection is NOT permitted. Do NOT
    return any value (except an empty dictionary) if disconnect is allowed. Because, at
    least until PSA social_core v.1.5.0, any returned value (e.g., Boolean) will result
    in ignoring the rest of the disconnect pipeline.
    See the following condition in `run_pipeline` function:
    https://github.com/python-social-auth/social-core/blob/master/social_core/backends/base.py#L114
    :param name: name of the backend (e.g., google-openidconnect)
    :type user: galaxy.model.User
    :type user_storage: galaxy.model.UserAuthnzToken
    :type strategy: galaxy.authnz.psa_authnz.Strategy
    :type backend: PSA backend object (e.g., social_core.backends.google_openidconnect.GoogleOpenIdConnect)
    :type request: webob.multidict.MultiDict
    :type details: dict
    :return: empty dict
    """
    pass


def disconnect(name=None, user=None, user_storage=None, strategy=None,
               backend=None, request=None, details=None, **kwargs):
    """
    Disconnect is the process of disassociating a Galaxy user and a third-party authnz.
    In other words, it is the process of removing any access and/or ID tokens of a user.
    :param name: name of the backend (e.g., google-openidconnect)
    :type user: galaxy.model.User
    :type user_storage: galaxy.model.UserAuthnzToken
    :type strategy: galaxy.authnz.psa_authnz.Strategy
    :type backend: PSA backend object (e.g., social_core.backends.google_openidconnect.GoogleOpenIdConnect)
    :type request: webob.multidict.MultiDict
    :type details: dict
    :return: void or empty dict. Any key-value pair inside the dictionary will be available
    inside PSA only, and will be passed to the next step in the disconnect pipeline. However,
    the key-value pair will not be returned as a result of calling the `do_disconnect` function.
    Additionally, returning any value except for a(n) (empty) dictionary, will break the
    disconnect pipeline, and that value will be returned as a result of calling the `do_disconnect` function.
    """
    user_authnz = strategy.trans.sa_session.query(user_storage).filter(user_storage.table.c.user_id == user.id,
                                                                       user_storage.table.c.provider == name).first()
    if user_authnz is None:
        return {'success': False, 'message': 'Not authenticated by any identity providers.'}
    # option A
    strategy.trans.sa_session.delete(user_authnz)
    # option B
    # user_authnz.extra_data = None
    strategy.trans.sa_session.flush()
