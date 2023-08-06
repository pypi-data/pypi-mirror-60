# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ccautils']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'ccautils',
    'version': '0.1.1',
    'description': 'A set of useful utilities for python programs',
    'long_description': None,
    'author': 'ccdale',
    'author_email': 'chris.charles.allison+ccautils@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
