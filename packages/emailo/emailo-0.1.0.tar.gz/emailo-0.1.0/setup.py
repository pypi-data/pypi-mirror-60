# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['emailo']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['emailo = emailo.console:app']}

setup_kwargs = {
    'name': 'emailo',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Vlad Dmitrievich',
    'author_email': 'me@2tunnels.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
