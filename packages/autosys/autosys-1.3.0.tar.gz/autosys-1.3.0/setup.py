# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autosys']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.4.4,<3.0.0', 'pytest>=5.3.5,<6.0.0', 'requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'autosys',
    'version': '1.3.0',
    'description': 'System utilities for Python on macOS',
    'long_description': None,
    'author': 'skeptycal',
    'author_email': 'skeptycal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
