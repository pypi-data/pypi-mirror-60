# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyuque', 'pyuque.util']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'pyuque',
    'version': '0.1.1',
    'description': 'A Python client for yuque.',
    'long_description': None,
    'author': None,
    'author_email': None,
    'url': 'https://github.com/socrateslee/pyuque',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
