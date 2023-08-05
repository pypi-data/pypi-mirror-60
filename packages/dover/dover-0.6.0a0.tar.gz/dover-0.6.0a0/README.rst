dover v0.6.0-alpha
==================

|version-badge| |codacy-coverage| |codacy-badge|

A commandline utility for incrementing your project version numbers.


Installation
^^^^^^^^^^^^

.. code-block:: text
    
    ... pip install dover


What does it do?
^^^^^^^^^^^^^^^^

When ``dover`` is run from the root directory of your project, it does the 
following:

    1. looks for a configuration file (``.dover``, ``.dover.ini``, ``setup.cfg``, ``pyproject.toml``)
    2. reads any ``dover`` configuration line in this format:

       .. code-block:: text
            
           [dover:file:relatvie/file.pth]

    Or in the case of ``pyproject.toml``:

       .. code-block:: text

           [tool.dover]
           versioned_files = ["pyproject.toml", "dover/cli.py"]

    3. searches the configured file references for "version" strings
    4. validates all version strings across all configured files.
    5. displays and/or increments the version strings based upon 
       cli options. 

Usage
^^^^^

.. code-block:: text 
    
    ... dover --help

    dover v0.6.0-alpha

    dover is a commandline utility for
    tracking and incrementing your
    project version numbers.

    Usage:
      dover [--list] [--debug] [--format=<fmt>]
      dover increment ((--major|--minor|--patch)
                       [--dev|--alpha|--beta|--rc] |
                       [--major|--minor|--patch]
                       (--dev|--alpha|--beta|--rc) | --release)
                       [--apply] [--debug] [--no-list] [--format=<fmt>]

    Options:
      -M --major      Update major version segment.
      -m --minor      Update minor version segment.
      -p --patch      Update patch version segment.
      -d --dev        Update dev version segment.
      -a --alpha      Update alpha pre-release segment.
      -b --beta       Update beta pre-release segment.
      -r --rc         Update release candidate segment.
      -R --release    Clear pre-release version.
      -x --no-list    Do not list files.
      --format=<fmt>  Apply format string.
      --debug         Print full exception info.
      -h --help       Display this help message
      --version       Display dover version.


.. |version-badge| image:: https://img.shields.io/badge/version-v0.6.0-alpha-green.svg

.. |codacy-badge| image:: https://api.codacy.com/project/badge/Grade/b92162d5dce1431caac8dcece168b0f4
                  :target: https://www.codacy.com/app/bitbucket_9/dover?utm_source=mgemmill@bitbucket.org&amp;utm_medium=referral&amp;utm_content=mgemmill/dover&amp;utm_campaign=Badge_Grade

.. |codacy-coverage| image:: https://api.codacy.com/project/badge/Coverage/b92162d5dce1431caac8dcece168b0f4
                     :target: https://www.codacy.com/app/bitbucket_9/dover?utm_source=mgemmill@bitbucket.org&amp;utm_medium=referral&amp;utm_content=mgemmill/dover&amp;utm_campaign=Badge_Coverage


See `Read  The Docs <http://dover.readthedocs.io/en/latest/>`_ for more.
