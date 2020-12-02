###################
tslide  v0.99
###################

.. image:: https://badge.fury.io/py/tslide.svg
    :target: https://badge.fury.io/py/tslide

.. image:: https://travis-ci.org/FNNDSC/tslide.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/tslide

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/tslide

.. contents:: Table of Contents

********
Overview
********

This repository provides ``tslide`` -- a python engine that builds an html/js/css slide show about a series of text files.

tslide
=======

``tslide`` was created to facilitate the rapid creation of "good enough" looking web-based slide shows where individual slides are created as separate stand-alone text files, one file per slide. The order of slides in the presentation is often just the ``ls`` order of the text files.


************
Installation
************

Installation is relatively straightforward, and we recommend using python ``pip`` to simply install the module, preferably in a python virtual environment.

Python Virtual Environment
==========================

On Ubuntu, install the Python virtual environment creator

.. code-block:: bash

  sudo apt install virtualenv

Then, create a directory for your virtual environments e.g.:

.. code-block:: bash

  mkdir ~/python-envs

You might want to add to your .bashrc file these two lines:

.. code-block:: bash

    export WORKON_HOME=~/python-envs
    source /usr/local/bin/virtualenvwrapper.sh

Note that depending on distro, the virtualenvwrapper.sh path might be

.. code-block:: bash

    /usr/share/virtualenvwrapper/virtualenvwrapper.sh

Subsequently, you can source your ``.bashrc`` and create a new Python3 virtual environment:

.. code-block:: bash

    source .bashrc
    mkvirtualenv --python=python3 python_env

To activate or "enter" the virtual env:

.. code-block:: bash

    workon python_env

To deactivate virtual env:

.. code-block:: bash

    deactivate

Install the module

.. code-block:: bash
 
    pip install tslide



Command line arguments
======================

.. code-block:: html


        [-x|--desc]                                     
        Provide an overview help page.

        [-y|--synopsis]
        Provide a synopsis help summary.

        [--version]
        Print internal version number and exit.

        [--debugToDir <dir>]
        A directory to contain various debugging output -- these are typically
        JSON object strings capturing internal state. If empty string (default)
        then no debugging outputs are captured/generated. If specified, then
        ``pfcon`` will check for dir existence and attempt to create if
        needed.

        [-v|--verbosity <level>]
        Set the verbosity level. "0" typically means no/minimal output. Allows for
        more fine tuned output control as opposed to '--quiet' that effectively
        silences everything.

EXAMPLES

.. code-block:: bash

    tslide                                                \\

