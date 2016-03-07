import ConfigParser

import os
import json
import stat
import random
import tempfile
from subprocess import Popen, PIPE

from galaxy.util.bunch import Bunch
from galaxy import web
from galaxy.managers import api_keys
from galaxy.tools.deps.docker_util import DockerVolume

import logging
log = logging.getLogger(__name__)


class InteractiveEnvironmentRequest(object):

    def __init__(self, trans, plugin):
        self.trans = trans
        self.log = log

        self.attr = Bunch()
        self.attr.viz_id = plugin.name
        self.attr.history_id = trans.security.encode_id( trans.history.id )
        self.attr.galaxy_config = trans.app.config
        self.attr.galaxy_root_dir = os.path.abspath(self.attr.galaxy_config.root)
        self.attr.root = web.url_for("/")
        self.attr.app_root = self.attr.root + "plugins/interactive_environments/" + self.attr.viz_id + "/static/"
        self.attr.import_volume = True

        plugin_path = os.path.abspath( plugin.path )

        # Store our template and configuration path
        self.attr.our_config_dir = os.path.join(plugin_path, "config")
        self.attr.our_template_dir = os.path.join(plugin_path, "templates")
        self.attr.HOST = trans.request.host.rsplit(':', 1)[0]

        self.load_deploy_config()
        self.attr.docker_hostname = self.attr.viz_config.get("docker", "docker_hostname")

        # Generate per-request passwords the IE plugin can use to configure
        # the destination container.
        self.notebook_pw_salt = self.generate_password(length=12)
        self.notebook_pw = self.generate_password(length=24)

        ie_parent_temp_dir = self.attr.viz_config.get("docker", "docker_galaxy_temp_dir") or None
        self.temp_dir = os.path.abspath( tempfile.mkdtemp( dir=ie_parent_temp_dir ) )

        if self.attr.viz_config.getboolean("docker", "wx_tempdir"):
            # Ensure permissions are set
            try:
                os.chmod( self.temp_dir, os.stat(self.temp_dir).st_mode | stat.S_IXOTH )
            except Exception:
                log.error( "Could not change permissions of tmpdir %s" % self.temp_dir )
                # continue anyway

        # This duplicates the logic in the proxy manager
        if self.attr.galaxy_config.dynamic_proxy_external_proxy:
            slash = '/'
            if self.attr.galaxy_config.cookie_path.endswith('/'):
                slash = ''
            self.attr.proxy_prefix = '%s%s%s' % (
                self.attr.galaxy_config.cookie_path,
                slash,
                self.attr.galaxy_config.dynamic_proxy_prefix)
        else:
            self.attr.proxy_prefix = ''

    def load_deploy_config(self, default_dict={}):
        # For backwards compat, any new variables added to the base .ini file
        # will need to be recorded here. The ConfigParser doesn't provide a
        # .get() that will ignore missing sections, so we must make use of
        # their defaults dictionary instead.
        default_dict = {
            'command': 'docker {docker_args}',
            'command_inject': '--sig-proxy=true -e DEBUG=false',
            'docker_hostname': 'localhost',
            'wx_tempdir': 'False',
            'docker_galaxy_temp_dir': None
        }
        viz_config = ConfigParser.SafeConfigParser(default_dict)
        conf_path = os.path.join( self.attr.our_config_dir, self.attr.viz_id + ".ini" )
        if not os.path.exists( conf_path ):
            conf_path = "%s.sample" % conf_path
        viz_config.read( conf_path )
        self.attr.viz_config = viz_config

        def _boolean_option(option, default=False):
            if self.attr.viz_config.has_option("main", option):
                return self.attr.viz_config.getboolean("main", option)
            else:
                return default

        # Older style port range proxying - not sure we want to keep these around or should
        # we always assume use of Galaxy dynamic proxy? None of these need to be specified
        # if using the Galaxy dynamic proxy.
        self.attr.PASSWORD_AUTH = _boolean_option("password_auth")
        self.attr.SSL_URLS = _boolean_option("ssl")

    def get_conf_dict(self):
        """
            Build up a configuration dictionary that is standard for ALL IEs.

            TODO: replace hashed password with plaintext.
        """
        trans = self.trans
        request = trans.request
        api_key = api_keys.ApiKeyManager( trans.app ).get_or_create_api_key( trans.user )
        conf_file = {
            'history_id': self.attr.history_id,
            'api_key': api_key,
            'remote_host': request.remote_addr,
            # DOCKER_PORT is NO LONGER AVAILABLE. All IEs must update.
            'cors_origin': request.host_url,
            'user_email': self.trans.user.email,
            'proxy_prefix': self.attr.proxy_prefix,
        }

        web_port = self.attr.galaxy_config.galaxy_infrastructure_web_port
        conf_file['galaxy_web_port'] = web_port or self.attr.galaxy_config.guess_galaxy_port()

        if self.attr.viz_config.has_option("docker", "galaxy_url"):
            conf_file['galaxy_url'] = self.attr.viz_config.get("docker", "galaxy_url")
        elif self.attr.galaxy_config.galaxy_infrastructure_url_set:
            conf_file['galaxy_url'] = self.attr.galaxy_config.galaxy_infrastructure_url.rstrip('/') + '/'
        else:
            conf_file['galaxy_url'] = request.application_url.rstrip('/') + '/'
            # Galaxy paster port is deprecated
            conf_file['galaxy_paster_port'] = conf_file['galaxy_web_port']

        return conf_file

    def generate_hex(self, length):
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))

    def generate_password(self, length):
        """
            Generate a random alphanumeric password
        """
        return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(length))

    def javascript_boolean(self, python_boolean):
        """
            Convenience function to convert boolean for use in JS
        """
        if python_boolean:
            return "true"
        else:
            return "false"

    def url_template(self, url_template):
        """Process a URL template

        There are several variables accessible to the user:

            - ${PROXY_URL} will be replaced with the dynamically create proxy's url
            - ${PROXY_PREFIX} will be replaced with the prefix that may occur
        """
        # Next several lines for older style replacements (not used with Galaxy dynamic
        # proxy)
        if self.attr.SSL_URLS:
            protocol = 'https'
        else:
            protocol = 'http'

        url_template = url_template.replace('${PROTO}', protocol) \
            .replace('${HOST}', self.attr.HOST)

        # Only the following replacements are used with Galaxy dynamic proxy
        # URLs
        url = url_template.replace('${PROXY_URL}', str(self.attr.proxy_url)) \
            .replace('${PROXY_PREFIX}', str(self.attr.proxy_prefix.replace('/', '%2F')))
        return url

    def volume(self, host_path, container_path, **kwds):
        return DockerVolume(host_path, container_path, **kwds)

    def docker_cmd(self, env_override={}, volumes=[]):
        """
            Generate and return the docker command to execute
        """
        temp_dir = self.temp_dir
        conf = self.get_conf_dict()
        conf.update(env_override)
        env_str = ' '.join(['-e "%s=%s"' % (key.upper(), item) for key, item in conf.items()])
        volume_str = ' '.join(['-v "%s"' % volume for volume in volumes])
        import_volume_str = '-v "{temp_dir}:/import/"'.format(temp_dir=temp_dir) if self.attr.import_volume else ''
        # This is the basic docker command such as "sudo -u docker docker {docker_args}"
        # or just "docker {docker_args}"
        command = self.attr.viz_config.get("docker", "command")
        # Then we format in the entire docker command in place of
        # {docker_args}, so as to let the admin not worry about which args are
        # getting passed
        command = command.format(docker_args='run {command_inject} {environment} -d -P {import_volume_str} {volume_str} {image}')
        # Once that's available, we format again with all of our arguments
        command = command.format(
            command_inject=self.attr.viz_config.get("docker", "command_inject"),
            environment=env_str,
            import_volume_str=import_volume_str,
            volume_str=volume_str,
            image=self.attr.viz_config.get("docker", "image")
        )
        return command

    def launch(self, raw_cmd=None, env_override={}, volumes=[]):
        if raw_cmd is None:
            raw_cmd = self.docker_cmd(env_override=env_override, volumes=volumes)
        log.info("Starting docker container for IE {0} with command [{1}]".format(
            self.attr.viz_id,
            raw_cmd
        ))
        p = Popen( raw_cmd, stdout=PIPE, stderr=PIPE, close_fds=True, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            log.error( "%s\n%s" % (stdout, stderr) )
            return None
        else:
            container_id = stdout
            log.debug( "Container id: %s" % container_id)
            inspect_data = self.inspect_container(container_id)
            port_mappings = self.get_container_port_mapping(inspect_data)
            if self.attr.docker_hostname == 'localhost':
                self.attr.docker_hostname = self.get_container_gateway_ip(inspect_data)
            if len(port_mappings) > 1:
                log.warning("Don't know how to handle proxies to containers with multiple exposed ports. Arbitrarily choosing first")
            elif len(port_mappings) == 0:
                log.warning("No exposed ports to map! Images MUST EXPOSE")
                return None
            # Fetch the first port_mapping
            (service, host_ip, host_port) = port_mappings[0]

            # Now we configure our proxy_requst object and we manually specify
            # the port to map to and ensure the proxy is available.
            self.attr.proxy_request = self.trans.app.proxy_manager.setup_proxy(
                self.trans,
                host=self.attr.docker_hostname,
                port=host_port,
                proxy_prefix=self.attr.proxy_prefix,
            )
            # These variables then become available for use in templating URLs
            self.attr.proxy_url = self.attr.proxy_request[ 'proxy_url' ]
            # Commented out because it needs to be documented and visible that
            # this variable was moved here. Usually would remove commented
            # code, but again, needs to be clear where this went. Remove at a
            # later time.
            #
            # PORT is no longer exposed internally. All requests are forced to
            # go through the proxy we ship.
            # self.attr.PORT = self.attr.proxy_request[ 'proxied_port' ]

    def inspect_container(self, container_id):
        """Runs docker inspect on a container and returns json response as python dictionary inspect_data.

        :type container_id: str
        :param container_id: a docker container ID

        :returns: inspect_data, a dict of docker inspect output
        """
        command = self.attr.viz_config.get("docker", "command")
        command = command.format(docker_args="inspect %s" % container_id)
        log.info("Inspecting docker container {0} with command [{1}]".format(
            container_id,
            command
        ))

        p = Popen(command, stdout=PIPE, stderr=PIPE, close_fds=True, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            log.error( "%s\n%s" % (stdout, stderr) )
            return None

        inspect_data = json.loads(stdout)
        # [{
        #     "NetworkSettings" : {
        #         "Ports" : {
        #             "3306/tcp" : [
        #                 {
        #                     "HostIp" : "127.0.0.1",
        #                     "HostPort" : "3306"
        #                 }
        #             ]
        return inspect_data

    def get_container_gateway_ip(self, inspect_data):
        """
        Returns gateway ip from inspect_data
        :type inspect_data: dict
        :param inspect_data: output of docker inspect
        :returns: gateway_ip
        """
        gateway_ip = inspect_data[0]['NetworkSettings']['Gateway']
        return gateway_ip

    def get_container_port_mapping(self, inspect_data):
        """
        :type inspect_data: dict
        :param inspect_data: output of docker inspect
        :returns: a list of triples containing (internal_port, external_ip,
                  external_port), of which the ports are probably the only
                  useful information.

        Someday code that calls this should be refactored whenever we get
        containers with multiple ports working.
        """
        mappings = []
        port_mappings = inspect_data[0]['NetworkSettings']['Ports']
        for port_name in port_mappings:
            for binding in port_mappings[port_name]:
                mappings.append((
                    port_name.replace('/tcp', '').replace('/udp', ''),
                    binding['HostIp'],
                    binding['HostPort']
                ))
        return mappings
