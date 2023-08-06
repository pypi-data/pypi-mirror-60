# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nnsplit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nnsplit',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Benjamin Minixhofer',
    'author_email': 'bminixhofer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
