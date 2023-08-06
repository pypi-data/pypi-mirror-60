# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ridicule']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ridicule',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'd1618033',
    'author_email': 'd1618033@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
