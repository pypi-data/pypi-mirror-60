# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['irb_kernel']

package_data = \
{'': ['*']}

install_requires = \
['notebook>=6.0.3,<7.0.0', 'pexpect>=4.8.0,<5.0.0']

setup_kwargs = {
    'name': 'irb-kernel',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kozo Nishida',
    'author_email': 'knishida@riken.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
