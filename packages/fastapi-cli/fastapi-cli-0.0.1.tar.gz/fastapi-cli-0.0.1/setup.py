# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fastapi_cli']

package_data = \
{'': ['*']}

install_requires = \
['importlib_metadata>=1.5,<2.0']

setup_kwargs = {
    'name': 'fastapi-cli',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Sebastián Ramírez',
    'author_email': 'tiangolo@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
