# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitsemver']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<20.0.0', 'pyyaml>=5.3,<6.0']

entry_points = \
{'console_scripts': ['gitsemver = gitsemver:main']}

setup_kwargs = {
    'name': 'gitsemver',
    'version': '0.3.5',
    'description': 'semantic versioning from git logs',
    'long_description': None,
    'author': 'Allen Lawrence',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
