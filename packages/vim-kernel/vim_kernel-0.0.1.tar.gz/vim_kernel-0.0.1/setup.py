# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vim_kernel']

package_data = \
{'': ['*'], 'vim_kernel': ['autoload/*']}

install_requires = \
['notebook>=6.0.3,<7.0.0']

setup_kwargs = {
    'name': 'vim-kernel',
    'version': '0.0.1',
    'description': 'A Jupyter kernel for Vim script',
    'long_description': None,
    'author': 'mattn',
    'author_email': 'mattn.jp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
