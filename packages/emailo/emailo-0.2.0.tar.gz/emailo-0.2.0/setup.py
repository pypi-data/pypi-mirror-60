# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['emailo']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'email_validator>=1.0.5,<2.0.0']

entry_points = \
{'console_scripts': ['emailo = emailo.console:app']}

setup_kwargs = {
    'name': 'emailo',
    'version': '0.2.0',
    'description': '',
    'long_description': "# emailo\n\n[![Build Status](https://travis-ci.org/2tunnels/emailo.svg?branch=master)](https://travis-ci.org/2tunnels/emailo)\n[![codecov](https://codecov.io/gh/2tunnels/emailo/branch/master/graph/badge.svg)](https://codecov.io/gh/2tunnels/emailo)\n\nemailo is a command line tool for parsing and analyzing emails from different files.\nMight be helpful for scraping and investigating dumps from breaches.\n\n## Installation\n\nemailo is a Python package, so I strongly recommend you to install it in separate `virtualenv`.\n\n```sh\n$ pip install emailo\n```\n\n## Parse\n\nParsing simple SQL dump:\n\n```sh\n$ emailo parse ~/Dumps/example.sql\njohn@example.com\nbill@example.net\nalex@example.org\ntroy@example.com\n...\n```\n\nYou can filter emails by domain using `endswith` options like so:\n\n```sh\n$ emailo parse ~/Dumps/example.sql --endswith=@example.com\njohn@example.com\ntroy@example.com\n...\n```\n\nemailo will output emails in `stdout`, don't forget to save them somewhere:\n\n```sh\n$ emailo parse ~/Dumps/example.sql > emails.txt\n```\n\n## Domains\n\nSometimes you need to know which domains are most popular in your email list:\n\n```sh\n$ emailo domains ~/Lists/emails.txt\nexample.com 2\nexample.net 1\nexample.org 1\n```\n\nOr you can get percentage value:\n\n```sh\n$ emailo domains ~/Lists/emails.txt --percentage\nexample.com 50.00%\nexample.net 25.00%\nexample.org 25.00%\n```\n\n## New feature request\n\nIf there is a missing functionality that you need, don't hesitate to create an [issue](https://github.com/2tunnels/emailo/issues).\n",
    'author': 'Vlad Dmitrievich',
    'author_email': 'me@2tunnels.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/2tunnels/emailo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
