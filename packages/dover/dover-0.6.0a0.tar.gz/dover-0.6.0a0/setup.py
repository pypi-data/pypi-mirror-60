# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dover']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.3,<0.5.0', 'docopt-ng>=0.7.2,<0.8.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['dover = dover.cli:main']}

setup_kwargs = {
    'name': 'dover',
    'version': '0.6.0a0',
    'description': 'Do version - track and update your package version.',
    'long_description': 'dover v0.6.0-alpha\n==================\n\n|version-badge| |codacy-coverage| |codacy-badge|\n\nA commandline utility for incrementing your project version numbers.\n\n\nInstallation\n^^^^^^^^^^^^\n\n.. code-block:: text\n    \n    ... pip install dover\n\n\nWhat does it do?\n^^^^^^^^^^^^^^^^\n\nWhen ``dover`` is run from the root directory of your project, it does the \nfollowing:\n\n    1. looks for a configuration file (``.dover``, ``.dover.ini``, ``setup.cfg``, ``pyproject.toml``)\n    2. reads any ``dover`` configuration line in this format:\n\n       .. code-block:: text\n            \n           [dover:file:relatvie/file.pth]\n\n    Or in the case of ``pyproject.toml``:\n\n       .. code-block:: text\n\n           [tool.dover]\n           versioned_files = ["pyproject.toml", "dover/cli.py"]\n\n    3. searches the configured file references for "version" strings\n    4. validates all version strings across all configured files.\n    5. displays and/or increments the version strings based upon \n       cli options. \n\nUsage\n^^^^^\n\n.. code-block:: text \n    \n    ... dover --help\n\n    dover v0.6.0-alpha\n\n    dover is a commandline utility for\n    tracking and incrementing your\n    project version numbers.\n\n    Usage:\n      dover [--list] [--debug] [--format=<fmt>]\n      dover increment ((--major|--minor|--patch)\n                       [--dev|--alpha|--beta|--rc] |\n                       [--major|--minor|--patch]\n                       (--dev|--alpha|--beta|--rc) | --release)\n                       [--apply] [--debug] [--no-list] [--format=<fmt>]\n\n    Options:\n      -M --major      Update major version segment.\n      -m --minor      Update minor version segment.\n      -p --patch      Update patch version segment.\n      -d --dev        Update dev version segment.\n      -a --alpha      Update alpha pre-release segment.\n      -b --beta       Update beta pre-release segment.\n      -r --rc         Update release candidate segment.\n      -R --release    Clear pre-release version.\n      -x --no-list    Do not list files.\n      --format=<fmt>  Apply format string.\n      --debug         Print full exception info.\n      -h --help       Display this help message\n      --version       Display dover version.\n\n\n.. |version-badge| image:: https://img.shields.io/badge/version-v0.6.0-alpha-green.svg\n\n.. |codacy-badge| image:: https://api.codacy.com/project/badge/Grade/b92162d5dce1431caac8dcece168b0f4\n                  :target: https://www.codacy.com/app/bitbucket_9/dover?utm_source=mgemmill@bitbucket.org&amp;utm_medium=referral&amp;utm_content=mgemmill/dover&amp;utm_campaign=Badge_Grade\n\n.. |codacy-coverage| image:: https://api.codacy.com/project/badge/Coverage/b92162d5dce1431caac8dcece168b0f4\n                     :target: https://www.codacy.com/app/bitbucket_9/dover?utm_source=mgemmill@bitbucket.org&amp;utm_medium=referral&amp;utm_content=mgemmill/dover&amp;utm_campaign=Badge_Coverage\n\n\nSee `Read  The Docs <http://dover.readthedocs.io/en/latest/>`_ for more.\n',
    'author': 'Mark Gemmill',
    'author_email': 'dev@markgemmill.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mgemmill-pypi/dover',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
