from os import listdir
from os.path import join, islink, realpath, basename, exists

from ..resolvers import (
    DependencyResolver,
    INDETERMINATE_DEPENDENCY,
    Dependency,
    ListableDependencyResolver,
)
from .resolver_mixins import UsesToolDependencyDirMixin

import logging
log = logging.getLogger( __name__ )


class BaseGalaxyPackageDependencyResolver(DependencyResolver, UsesToolDependencyDirMixin):
    dict_collection_visible_keys = DependencyResolver.dict_collection_visible_keys + ['base_path', 'versionless']

    def __init__(self, dependency_manager, **kwds):
        # Galaxy tool shed requires explicit versions on XML elements,
        # this in inconvient for testing or Galaxy instances not utilizing
        # the tool shed so allow a fallback version of the Galaxy package
        # resolver that will just grab 'default' version of exact version
        # unavailable.
        self.versionless = str(kwds.get('versionless', "false")).lower() == "true"
        self._init_base_path( dependency_manager, **kwds )

    def resolve( self, name, version, type, **kwds ):
        """
        Attempt to find a dependency named `name` at version `version`. If version is None, return the "default" version as determined using a
        symbolic link (if found). Returns a triple of: env_script, base_path, real_version
        """
        if version is None or self.versionless:
            exact = not self.versionless or version is None
            return self._find_dep_default( name, type=type, exact=exact, **kwds )
        else:
            return self._find_dep_versioned( name, version, type=type, **kwds )

    def _find_dep_versioned( self, name, version, type='package', **kwds ):
        base_path = self.base_path
        path = join( base_path, name, version )
        return self._galaxy_package_dep(path, version, True)

    def _find_dep_default( self, name, type='package', exact=True, **kwds ):
        base_path = self.base_path
        path = join( base_path, name, 'default' )
        if islink( path ):
            real_path = realpath( path )
            real_version = basename( real_path )
            return self._galaxy_package_dep(real_path, real_version, exact)
        else:
            return INDETERMINATE_DEPENDENCY

    def _galaxy_package_dep( self, path, version, exact ):
        script = join( path, 'env.sh' )
        if exists( script ):
            return GalaxyPackageDependency(script, path, version, exact)
        elif exists( join( path, 'bin' ) ):
            return GalaxyPackageDependency(None, path, version, exact)
        return INDETERMINATE_DEPENDENCY


class GalaxyPackageDependencyResolver(BaseGalaxyPackageDependencyResolver, ListableDependencyResolver):
    resolver_type = "galaxy_packages"

    def list_dependencies(self):
        base_path = self.base_path
        for package_name in listdir(base_path):
            package_dir = join(base_path, package_name)
            for version in listdir(package_dir):
                version_dir = join(package_dir, version)
                if version == "default":
                    version = None
                valid_dependency = _is_dependency_directory(version_dir)
                if valid_dependency:
                    yield self._to_requirement(package_name, version)


def _is_dependency_directory(directory):
    return exists(join(directory, 'env.sh')) or exists(join(directory, 'bin'))


class GalaxyPackageDependency(Dependency):
    dict_collection_visible_keys = Dependency.dict_collection_visible_keys + ['script', 'path', 'version']
    dependency_type = 'galaxy_package'

    def __init__( self, script, path, version, exact=True ):
        self.script = script
        self.path = path
        self.version = version
        self._exact = exact

    @property
    def exact(self):
        return self._exact

    def shell_commands( self, requirement ):
        base_path = self.path
        if self.script is None and base_path is None:
            log.warn( "Failed to resolve dependency on '%s', ignoring", requirement.name )
            commands = None
        elif requirement.type == 'package' and self.script is None:
            commands = 'PACKAGE_BASE=%s; export PACKAGE_BASE; PATH="%s/bin:$PATH"; export PATH' % ( base_path, base_path )
        else:
            commands = 'PACKAGE_BASE=%s; export PACKAGE_BASE; . %s' % ( base_path, self.script )
        return commands

__all__ = ['GalaxyPackageDependencyResolver', 'GalaxyPackageDependency']
