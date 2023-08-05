# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hashversion']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'gitpython>=3.0.5,<4.0.0', 'toml>=0.10.0,<0.11.0']

extras_require = \
{'docs': ['sphinx>=2.3.1,<3.0.0',
          'sphinx-rtd-theme>=0.4.3,<0.5.0',
          'm2r>=0.2.1,<0.3.0']}

entry_points = \
{'console_scripts': ['hashver = hashversion.cli:cli']}

setup_kwargs = {
    'name': 'hashversion',
    'version': '0.4.0',
    'description': 'Automate versioning and related requirements when using hashver',
    'long_description': '# Hash Version\n\n[![PyPI](https://img.shields.io/pypi/v/hashversion)](https://pypi.org/project/hashversion/)\n[![License](https://img.shields.io/github/license/miniscruff/hashversion-python.svg)](https://github.com/miniscruff/hashversion-python/blob/master/LICENSE)\n[![Issues](https://img.shields.io/github/issues/miniscruff/hashversion-python.svg)](https://github.com/miniscruff/hashversion-python/issues)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![codecov](https://codecov.io/gh/miniscruff/hashversion-python/branch/master/graph/badge.svg)](https://codecov.io/gh/miniscruff/hashversion-python)\n[![Documentation Status](https://readthedocs.org/projects/hashversion-python/badge/?version=latest)](https://hashversion-python.readthedocs.io/en/latest/?badge=latest)\n\nPython CLI for automating hash versioning and related requirements.\nTo help automate versioning, changelog management and other pieces of continuous\ndeployments.\n\nFull documentation can be viewed [here](https://hashversion-python.readthedocs.io/en/latest/).\nThis project is a python package build for hashver which is published [here](https://miniscruff.github.io/hashver/).\n\n## Quick Start\n... coming soon ...\n',
    'author': 'Ronnie Smith',
    'author_email': 'halfpint1170@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/miniscruff/hashversion-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
