# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywhere39']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

setup_kwargs = {
    'name': 'pywhere39',
    'version': '0.0.1',
    'description': 'Use BIP39 words to locate anywhere in the world',
    'long_description': None,
    'author': 'Dominik Kozaczko',
    'author_email': 'dominik@kozaczko.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
