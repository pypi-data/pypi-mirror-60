# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nnsplit']

package_data = \
{'': ['*'], 'nnsplit': ['data/*', 'data/de/*']}

install_requires = \
['numpy>=1,<2', 'torch>=1,<2']

setup_kwargs = {
    'name': 'nnsplit',
    'version': '0.1.3',
    'description': 'Fast, robust sentence splitting with bindings for Python, Rust and Javascript.',
    'long_description': None,
    'author': 'Benjamin Minixhofer',
    'author_email': 'bminixhofer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
