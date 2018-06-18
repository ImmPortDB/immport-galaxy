"""Utilities for constructing Galaxy integration tests.

Tests that start an actual Galaxy server with a particular configuration in
order to test something that cannot be tested with the default functional/api
tessting configuration.
"""
import os
from unittest import skip, TestCase

from galaxy.tools.deps.commands import which
from galaxy.tools.verify.test_data import TestDataResolver
from .api import UsesApiTestCaseMixin
from .driver_util import GalaxyTestDriver

NO_APP_MESSAGE = "test_case._app called though no Galaxy has been configured."


def skip_if_jenkins(cls):

    if os.environ.get("BUILD_NUMBER", ""):
        return skip

    return cls


def skip_unless_executable(executable):
    if which(executable):
        return lambda func: func
    return skip("PATH doesn't contain executable %s" % executable)


def skip_unless_docker():
    return skip_unless_executable("docker")


class IntegrationTestCase(TestCase, UsesApiTestCaseMixin):
    """Unit test case with utilities for spinning up Galaxy."""

    prefer_template_database = True
    # Subclasses can override this to force uwsgi for tests.
    require_uwsgi = False

    @classmethod
    def setUpClass(cls):
        """Configure and start Galaxy for a test."""
        cls._app_available = False
        cls._test_driver = GalaxyTestDriver()
        cls._prepare_galaxy()
        cls._test_driver.setup(config_object=cls)
        cls._app_available = True
        cls._configure_app()

    @classmethod
    def tearDownClass(cls):
        """Shutdown Galaxy server and cleanup temp directory."""
        cls._test_driver.tear_down()
        cls._app_available = False

    def setUp(self):
        self.test_data_resolver = TestDataResolver()
        # Setup attributes needed for API testing...
        server_wrapper = self._test_driver.server_wrappers[0]
        host = server_wrapper.host
        port = server_wrapper.port
        self.url = "http://%s:%s" % (host, port)
        self._setup_interactor()

    @property
    def _app(self):
        assert self._app_available, NO_APP_MESSAGE
        return self._test_driver.app

    @property
    def _tempdir(self):
        return self._test_driver.galaxy_test_tmp_dir

    @classmethod
    def _prepare_galaxy(cls):
        """Extension point for subclasses called before Galaxy is launched."""

    @classmethod
    def _configure_app(cls):
        """Extension point for subclasses called after Galaxy is launched.

        ```self._app``` can be used to access Galaxy core app.
        """

    @classmethod
    def handle_galaxy_config_kwds(cls, galaxy_config_kwds):
        """Extension point for subclasses to modify arguments used to configure Galaxy.

        This method will be passed the keyword argument pairs used to call
        Galaxy Config object and can modify the Galaxy instance created for
        the test as needed.
        """

    @classmethod
    def handle_uwsgi_cli_command(cls, command):
        """Extension point sub subclasses to modify arguments used to launch uWSGI server.

        Command will a list that can be modified.
        """

    def _run_tool_test(self, *args, **kwargs):
        return self._test_driver.run_tool_test(*args, **kwargs)
