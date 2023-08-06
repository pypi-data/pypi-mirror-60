# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pppiv']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'poetry>=1.0.3,<2.0.0']

entry_points = \
{'console_scripts': ['pppiv = pppiv.main:main']}

setup_kwargs = {
    'name': 'pppiv',
    'version': '0.1.0',
    'description': 'Poetry Python Path Injector for VSCode',
    'long_description': None,
    'author': 'Masahiro Wada',
    'author_email': 'argon.argon.argon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
