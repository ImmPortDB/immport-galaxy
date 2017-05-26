.. figure:: https://wiki.galaxyproject.org/Images/GalaxyLogo?action=AttachFile&do=get&target=galaxy_project_logo.jpg
   :alt: Galaxy Logo

The latest information about Galaxy is available via `https://galaxyproject.org/ <https://galaxyproject.org/>`__

.. image:: https://img.shields.io/badge/questions-galaxy%20biostar-blue.svg
    :target: https://biostar.usegalaxy.org
    :alt: Ask a question

.. image:: https://img.shields.io/badge/chat-irc.freenode.net%23galaxyproject-blue.svg
    :target: https://webchat.freenode.net/?channels=galaxyproject
    :alt: Chat with us

.. image:: https://img.shields.io/badge/docs-release-green.svg
    :target: https://docs.galaxyproject.org/en/master/
    :alt: Release Documentation

.. image:: https://travis-ci.org/galaxyproject/galaxy.svg?branch=dev
    :target: https://travis-ci.org/galaxyproject/galaxy
    :alt: Inspect the test results

Galaxy Quickstart
=================

Galaxy requires Python 2.7 To check your python version, run:

.. code:: console

    $ python -V
    Python 2.7.3

Start Galaxy:

.. code:: console

    $ sh run.sh

Once Galaxy completes startup, you should be able to view Galaxy in your
browser at:

http://localhost:8080

You may wish to make changes from the default configuration. This can be
done in the ``config/galaxy.ini`` file. Tools can be either installed
from the Tool Shed or added manually. For details please see the Galaxy
wiki:

https://wiki.galaxyproject.org/Admin/Tools/AddToolFromToolShedTutorial

Not all dependencies are included for the tools provided in the sample
``tool_conf.xml``. A full list of external dependencies is available at:

https://wiki.galaxyproject.org/Admin/Tools/ToolDependencies

Issues and Galaxy Development
=============================

Please see `CONTRIBUTING.md <CONTRIBUTING.md>`_ .

Roadmap
=============================

Interested in the next steps for Galaxy? Take a look here: https://github.com/galaxyproject/galaxy/issues/1928

ImmPort Galaxy Set up
=============================

To run the tools for ImmPort Galaxy smoothly, the following dependencies are required:

.. code:: console

    $ apt-get install gfortran g++
    $ apt-get install libreadline-dev libX11-dev xorg-dev python-dev
    $ apt-get install libcurl4-openssl-dev libxml2-dev libbz2-dev
    $ apt-get install liblzma-dev libpcre3-dev
    $ apt-get install libhdf5-serial-dev libhdf5-dev mesa-common-dev libglu1-mesa-dev

Install R:

.. code:: console

    $ curl -O  https://cran.r-project.org/src/base/R-3/R-3.4.0.tar.gz
    $ gzip -cd R-3.4.0.tar.gz | tar xvf -
    $ cd R-3.4.0
    $ ./configure --prefix=/home/galaxy/opt/R-3.4.0-Shared --with-tcltk --enable-R-shlib
    $ make
    $ make install

Add R to your PATH.
Within R, install the following packages:

.. code:: console

    >source("http://bioconductor.org/biocLite.R")
    >biocLite()
    >biocLite("flowCore") # version 1.42.0
    >biocLite("flowDensity") # version 1.10.0
    >biocLite("flowCL") # version 1.14.0
    >biocLite("flowAI") # version 1.4.2
    >install.packages("plyr",repos="http://cran.r-project.org")
    >install.packages("ggplot2",repos="http://cran.r-project.org")
    >biocLite("flowViz")
    >biocLite("ncdfFlow")
    >biocLite("rgl")
    >biocLite("ks")
    >biocLite("flowWorkspace")
    >biocLite("flowStats")
    >biocLite("flowVS")
    >biocLite("ggcyto") # version 1.5.1

Install required python packages in the galaxy virtual environment:

.. code:: console

    $ cd /home/galaxy/immport-galaxy
    $ . .venv/bin/activate
    $ pip install numpy==1.9.2
    $ pip install matplotlib
    $ pip install pandas==0/18.0
    $ pip install jinja2
    $ pip install rpy2
    $ pip install scipy==0.17.0
    $ pip install plotly==1.12.9

Compile FLOCK. The binaries are included in $GALAXY_HOME/tools/flowtools/src.

.. code:: console

    $ cd $GALAXY_HOME/tools/flowtools/bin
    $ cc -o flock1 ../src/flock1.c ../src/find_connected.c -lm
    $ cc -o flock2 ../src/flock2.c -lm
    $ cc -o cent_adjust ../src/cent_adjust.c -lm

ImmPort Galaxy supports auto-detection of FCS files, with the following dependency

.. code:: console

    $ conda config --add channels conda-forge
    $ conda config --add channels defaults
    $ conda config --add channels r
    $ conda config --add channels bioconda
    $ conda install ig-checkFCS

Feel free to contact the ImmPort Galaxy team if you have any questions: immport-galaxy@immport.org
