# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['config_pyrser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'config-pyrser',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'wadamek65',
    'author_email': 'wadamek65@gmail.com',
    'maintainer': 'wadamek65',
    'maintainer_email': 'wadamek65@gmail.com',
    'url': 'https://github.com/wadamek65/config-pyrser',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
