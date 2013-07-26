Requirements
============

* Jython 2.7 with setuptools 

    cd ~/jython2.7b1/bin
    wget http://peak.telecommunity.com/dist/ez_setup.py
    jython ez_setup.py

NOTE: a change has been made on PyPI that redirects HTTP to HTTPS. Jython
cannot handle HTTPS at this moment so this section below about setting up using
buildout doesn't work. My current workflow is to copy URL of package zip from
PyPI web page, wget it, and install using jython's `easy_install package.zip`


Setting up
==========

This is a Jython project, so use jython when performing the bootstrap step:

    jython bootstrap.py
    bin/buildout


Running
=======

    jython -m my_project.app
