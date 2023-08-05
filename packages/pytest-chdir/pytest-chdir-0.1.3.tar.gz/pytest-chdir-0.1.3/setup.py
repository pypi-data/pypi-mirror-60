# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pytest_chdir']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=5.0.0,<6.0.0']

entry_points = \
{'pytest11': ['pytest-chdir = pytest_chdir.plugin']}

setup_kwargs = {
    'name': 'pytest-chdir',
    'version': '0.1.3',
    'description': 'A pytest fixture for changing current working directory',
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
