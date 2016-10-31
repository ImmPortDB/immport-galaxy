=================================
Conda for Tool Dependencies
=================================

Galaxy tools (also called wrappers) traditionally use Tool Shed package
recipes to install their dependencies. At the tool's installation time
the recipe is downloaded and executed in order to provide the underlying
software executables. Introduction of these Galaxy-specific recipes was
a necessary step at the time, however nowadays there are other more
mature and stable options to install software in a similar manner. The
Galaxy community has taken steps to improve the tool dependency system
in order to enable new features and expand its reach. This document aims
to describe these and answer the FAQ.

Galaxy has adopted a new standard for tool dependencies: Conda packages!

Not only do Conda packages make tool dependencies more reliable and
stable, they are also easier to test and faster to develop than the
traditional Tool Shed package recipes.

Conda is a package manager like apt-get, yum, pip, brew or guix. We
don't want to argue about the relative merits of various package
managers here, in fact Galaxy supports multiple package managers and we
welcome community contributions (such as implementing a Guix package
manager or enhancing the existing brew support to bring it on par with
Conda).

As a community, we have decided that Conda is the one that best fulfills
our needs. The following are some of the crucial Conda features that led
to this decision:

-  Installation of packages does not require root privileges
   (Installation at any location the Galaxy user has write access to)
-  Multiple versions of software can be installed in parallel
-  HPC-ready
-  Faster and more robust package installations through p re-compiled
   packages (no build environment complications)
-  Independent of programming language ( R, Perl, Python, Julia, Java,
   pre-compiled binaries, and more )
-  Easy to write recipes (1 YAML description file + 1 Bash install
   script)
-  An active, large and growing community (with more and more software
   authors managing their own recipes)
-  Extensive documentation: `Conda documentation`_ and `Conda quick-start`_

Below we answer some common questions (collected by Lance Parsons):


1. How do I enable Conda dependency resolution for existing Galaxy installations?
*********************************************************************************

Most Galaxy administrators have not set up a dependency resolvers
configuration file ( ``dependency_resolvers_conf.xml`` ) which means they
are using Galaxy's default ( ``dependency_resolvers_conf.xml.sample`` ).
Galaxy has enabled Conda dependency resolution by default since release
16.04 (if Conda was installed already), so many existing installations
can use Conda dependencies. Having Conda enabled in ``dependency_resolvers_conf.xml`` means that Galaxy will
look for dependencies using the Conda system when it attempts to run
tools. If ``conda_auto_install`` is True , and a dependency is not found,
Galaxy will attempt to install it using the configured Conda channels. A
graphical user interface that allows administrators install Conda
packages directly from Galaxy when tools are installed from the Tool
Shed is available since the 16.07 version of Galaxy.

The most important configuration settings related to Conda are listed in Table 1.

+--------------------------+--------------------------+---------------------------+
| Setting                  | Default setting          | Meaning                   |
+--------------------------+--------------------------+---------------------------+
| ``conda_prefix``         | <tool\_dependency\_dir>/ | the location              |
|                          | \_conda                  | on the                    |
|                          |                          | filesystem where Conda    |
|                          |                          | packages and              |
|                          |                          | environments are          |
|                          |                          | installed                 |
|                          |                          |                           |
|                          |                          | IMPORTANT : Due to a      |
|                          |                          | current limitation in     |
|                          |                          | Conda, the total length   |
|                          |                          | of the                    |
|                          |                          |                           |
|                          |                          | ``conda_prefix`` and the  |
|                          |                          | ``job_working_directory`` |
|                          |                          | path should be less       |
|                          |                          | than 50 characters!       |
+--------------------------+--------------------------+---------------------------+
| ``conda_auto_install``   | False                    | Set to True to instruct   |
|                          |                          | Galaxy to look for and    |
|                          |                          | install Conda packages    |
|                          |                          | for missing tool          |
|                          |                          | dependencies before       |
|                          |                          | running a job             |
+--------------------------+--------------------------+---------------------------+
| ``conda_auto_init``      | False                    | Set to True to instruct   |
|                          |                          | Galaxy to install Conda   |
|                          |                          | automatically if it       |
|                          |                          | cannot find a local copy  |
+--------------------------+--------------------------+---------------------------+

*Table 1: Important configuration options for Conda in Galaxy*


2. How do Conda dependencies work? Where do things get installed?
*********************************************************************************

In contrast to the old dependency system, which was used exclusively by
Galaxy, Conda is a pre-existing, independent project. With Conda it
is possible for an admin to install packages without touching Galaxy at
all – managing your dependencies independently from Galaxy. Galaxy can
handle these dependencies for you, but admins are not required to use
Galaxy for dependency management.

There are a few new config options in the galaxy.ini file (see Table
1 or ``galaxy.ini.sample`` for more information), but by default Galaxy
will install Conda (the package manager) and the required packages in
the ``<tool_dependency_dir>/_conda/`` directory. In this directory,
Galaxy will create an ``envs`` folder with all of the environments managed
by Galaxy. Every environment contains a ``lib``, ``bin``, ``share``, and ``include``
subdirectory, depending on the tool, and is sufficient to get a Galaxy
tool up and running. Galaxy simply sources this folder via Conda and
makes everything available before the tool is executed on your cluster.

To summarize, there are four ways to manage Conda dependencies for use
with Galaxy. For all of these options, Conda dependency management must
be configured in the ``dependency_resolvers_conf.xml`` and the ``galaxy.ini`` file.

#. Manual Install - Conda dependencies may be installed by
   administrators from the command line. Conda (and thus the Conda
   environments) should be installed in the location specified by the
   ``conda_prefix`` path (defined in ``galaxy.ini`` and by default
   ``<tool_dependency_dir>/_conda/`` directory). Galaxy will search
   these environments for required packages when tools are run. Conda
   environment names have to follow a specific naming pattern. As an
   example, to install samtools in version 0.1.19, the administrator can
   run the command:

   .. code-block:: bash

      $ conda create --name __package__samtools@__version__0.1.19 samtools==0.1.19 --channel bioconda

   Tools that require samtools version 0.1.19 will then be able to find
   and use the installed Conda package.
#. Galaxy Admin Interface (>= 16.07) - Galaxy will install Conda tool
   dependencies when tools are installed from the Tool Shed if the
   option “When available, install externally managed dependencies (e.g.
   Conda)? Beta” is checked. Admins may also view and manage Conda
   dependencies via the Admin interface.
#. Automatically at tool run time - When a tool is run and a dependency
   is not found, Galaxy will attempt to install the dependency using
   Conda if ``conda_auto_install`` is activated in the configuration.
#. Via the API , upon tool installation (>= 16.07) - The Galaxy
   community maintains an `ansible role`_ that uses
   BioBlend_ and the Galaxy API to install tools.


3. What is required to make use of this? Any specific packages, Galaxy revision, OS version, etc.?
*********************************************************************************

The minimum required version of Galaxy to use Conda is 16.01, however
version 16.07 or greater is recommended. The 16.07 release of Galaxy has
a nice graphical user interface to manage packages, but this is not
required to have Conda dependencies managed and used by Galaxy.

Conda packages should work on all compatible operating systems with
glibc version (2.5) or newer (this includes Centos 5). We will most
likely switch soon to glibc version 2.12 as minimum requirement (this
includes CentOS 6). So all packages will run on all \*nix operating
systems newer than 2007.


4. How do I know what system is being used by a given tool?
*********************************************************************************

The Galaxy log will tell you which dependency resolution system is used
to satisfy each tool dependency and you can specify priorities using the
``config/dependency_resolution_conf.xml`` file. If you put Conda on
top, Galaxy will at first try to use Conda to resolve a tool dependency;
if this does not work, the following dependency resolvers is used, as
specified. See `resolver docs`_ for detailed documentation. Starting from galaxy release 16.07, you can
see which dependency will be used (“resolved”) in the admin panel.


5. How do I go about specifying Conda dependencies for a tool? All the docs still seem to recommend (or exclusively discuss) the ``tool_dependencies.xml`` method.
*********************************************************************************

The simple answer is: you don't need to do much to make Conda work for a tool.

The ``<requirement>`` tag in the tool XML file is enough. The name and the
version should correspond to a Conda package in the ``default``, ``r``,
``bioconda`` or ``iuc`` Conda channel (you can extend this list if you
like in your ``galaxy.ini`` ). If this is the case you are ready to go. Read
more about `Conda channels`_  and browse their packages on https://anaconda.org/ url followed by the channel name (e.g.
`https://anaconda.org/bioconda <https://anaconda.org/bioconda>`__
).

We will gradually adjust the documentation about ``tool_dependencies.xml`` and
deprecate it everywhere.


6. During tool installation what if there is no Conda package available for given requirement? What if the requirement is resolved in a different software than the original wrapper author meant to use?
*********************************************************************************

If there is no Conda package available during tool installation the tool
will install successfully, and can be used if its dependencies are
satisfied by another dependency system such as Tool Shed package
recipes, Docker containers or modules.

If there is a package of correct name and version it will be used. There
is no equivalent of the “owner” concept used in Galaxy packages
installed from the Tool Shed.


7. Where can I find a list of existing Conda packages that I can point to, so I don't have to reinvent the wheel for common dependencies?
*********************************************************************************

With Conda installed run:

.. code-block:: bash

   $ conda search <package_name> -c bioconda -c iuc

This will search in all channels that are activated by default in
Galaxy. If you find your package your are ready to go. If not please
`create a Conda package`_ and submit_ it to BioConda_ or get in `contact with the IUC`_.


8. How can I create a new Conda package for a dependency?
*********************************************************************************

Adding a package to the BioConda or IUC Conda channels will make it
available for Galaxy tools to use as a dependency. To learn how, get in
touch with the awesome BioConda community. They have great documentation
and assist with all development. You will also see a few of us at this
project to get you started :)

Don't be scared! Conda recipes are really simple to write. Conda also
offers you, so called \`skeleton\` generators, generating recipes from
pypi, cran, cpan for you (mostly) automatically.


9. Is there a way to convert traditional Tool Shed package recipes that are not yet in a Conda channel?
*********************************************************************************

First, you do not need to do anything to your wrapper as long as the
package name in the requirement tag matches the name of correct
Conda package. (You may want to mention in the README or a comment the
Conda channel that contains the package).

If you want to migrate some recipes from XML to Conda, IUC is happy to
give you a hand. We are trying to get all new versions under Conda and
leave the old versions as they are – simply because of time.


10. What is the recommendation for existing installations? Will I continue to maintain both systems or migrate to the new Conda system eventually?
*********************************************************************************

Old tools will use the traditional installation system, this system will
stay and will be supported to install old tools. This we promised to our
community to guarantee sustainability and reproducibility. New tools
from the IUC, may be Conda only.


11. If I have Conda enabled, what do I need to do to install tools using it? For example, how can I install the latest Trinity? And how will I know dependencies are installed?
*********************************************************************************

This depends on your ``galaxy.ini`` setting. Galaxy will install Conda for
you if you have enabled ``conda_auto_init``. If ``conda_auto_install`` is
enabled, Galaxy will install Trinity via Conda when a Trinity job is
launched and Trinity is not yet installed . With the latest 16.07
release you can see which dependencies are being used in the “Manage
installed tools” section of the admin panel and you can select whether
or not to install Conda packages or Tool Shed package recipes when you
install new tools, even if ``conda_auto_install`` is disabled.

More improvements to the UI will be coming in future releases. To see if Galaxy
has created a Trinity environment for you have a look at folder under
``<tool_dependency_dir>/_conda/envs/``.


12. Can I mix traditional Galaxy packages and Conda packages?
*********************************************************************************

Yes, the way this works is that Galaxy goes through the list of
requirements for a tool, and then determines for each requirement if it
can be satisfied by any of the active resolver systems.

The order in which resolvers are tried is listed in the
``dependency_resolvers_conf.xml`` file, and the default order is

-  Tool Shed packages
-  Packages manually installed by administrators
-  Conda packages

The first system that satisfies a requirement will be used.


13. What can I do if Conda doesn't work for me?
*********************************************************************************

There is currently a limitation in the way Conda packages are being
built. This limitation will be addressed shortly by the Conda community,
however this requires all packages to be rebuilt.

To work around this limitation, please make sure that the total length
of the ``conda_prefix`` and ``job_working_directory`` path is less than 50
characters long.

If this is your problem, you should see a warning similar to the
following in your galaxy log files:

.. code-block:: bash

   ERROR: placeholder '/home/ray/r_3_3_1-x64-3.5/envs/_build_placehold_placehold_placehold_placehold_pl' too short

In rare cases Conda may not have been properly installed by Galaxy.
A symptom for this is if there is no activate script in
``conda_prefix/bin`` folder. In that case you can delete the ``conda_prefix`` folder
and restart Galaxy, which will again attempt to install Conda.

If this does not solve your problem or you have any trouble following
the instructions, please ask on the Galaxy mailing list or the Galaxy
IRC channel.

.. _Conda documentation: http://conda.pydata.org/docs/building/build.html
.. _Conda quick-start: http://conda.pydata.org/docs/get-started.html
.. _ansible role: https://github.com/galaxyproject/ansible-galaxy-tools
.. _BioBlend: https://github.com/galaxyproject/bioblend
.. _resolver docs: https://docs.galaxyproject.org/en/master/admin/dependency_resolvers.html
.. _Conda channels: http://conda.pydata.org/docs/custom-channels.html
.. _create a Conda package: http://conda.pydata.org/docs/building/recipe.html#conda-recipe-files-overview
.. _submit: https://bioconda.github.io/#step-4-join-the-team
.. _BioConda: https://bioconda.github.io
.. _contact with the IUC: https://gitter.im/galaxy-iuc/iuc
