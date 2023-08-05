# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pythainav']

package_data = \
{'': ['*']}

install_requires = \
['requests-html>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'pythainav',
    'version': '0.1.0',
    'description': 'a Python interface to pull thai mutual fund NAV',
    'long_description': None,
    'author': 'Nutchanon Ninyawee',
    'author_email': 'me@nutchanon.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
