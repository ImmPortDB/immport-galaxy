from galaxy.util.dictifiable import Dictifiable

from ..requirements import ToolRequirement

from abc import ABCMeta, abstractmethod, abstractproperty


class DependencyResolver(Dictifiable, object):
    # Keys for dictification.
    dict_collection_visible_keys = ['resolver_type', 'resolves_simple_dependencies']
    # A "simple" dependency is one that does not depend on the the tool
    # resolving the dependency. Classic tool shed dependencies are non-simple
    # because the repository install context is used in dependency resolution
    # so the same requirement tags in different tools will have very different
    # resolution.
    resolves_simple_dependencies = True
    __metaclass__ = ABCMeta

    @abstractmethod
    def resolve( self, name, version, type, **kwds ):
        """
        Given inputs describing dependency in the abstract, yield tuple of
        (script, bin, version). Here script is the env.sh file to source
        before running a job, if that is not found the bin directory will be
        appended to the path (if it is not None). Finally, version is the
        resolved tool dependency version (which may differ from requested
        version for instance if the request version is 'default'.)
        """

    def _get_config_option(self, key, dependency_resolver, default=None, config_prefix=None, **kwds):
        """ Look in resolver-specific settings for option and then fallback to
        global settings.
        """
        global_key = "%s_%s" % (config_prefix, key)
        if key in kwds:
            return kwds.get(key)
        elif global_key in dependency_resolver.extra_config:
            return dependency_resolver.extra_config.get(global_key)
        else:
            return default


class ListableDependencyResolver:
    """ Mix this into a ``DependencyResolver`` and implement to indicate
    the dependency resolver can iterate over its dependencies and generate
    requirements.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_dependencies(self):
        """ List the "simple" requirements that may be resolved "exact"-ly
        by this dependency resolver.
        """

    def _to_requirement(self, name, version=None):
        return ToolRequirement(name=name, type="package", version=version)


class InstallableDependencyResolver:
    """ Mix this into a ``DependencyResolver`` and implement to indicate
    the dependency resolver can attempt to install new dependencies.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def install_dependency(self, name, version, type, **kwds):
        """ Attempt to install this dependency if a recipe to do so
        has been registered in some way.
        """


class Dependency(Dictifiable, object):
    dict_collection_visible_keys = ['dependency_type', 'exact']
    __metaclass__ = ABCMeta

    @abstractmethod
    def shell_commands( self, requirement ):
        """
        Return shell commands to enable this dependency.
        """

    @abstractproperty
    def exact( self ):
        """ Return true if version information wasn't discarded to resolve
        the dependency.
        """


class NullDependency( Dependency ):
    dependency_type = None
    exact = True

    def shell_commands( self, requirement ):
        return None


INDETERMINATE_DEPENDENCY = NullDependency()
