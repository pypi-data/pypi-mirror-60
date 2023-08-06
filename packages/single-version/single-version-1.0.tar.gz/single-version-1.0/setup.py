# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['single_version']

package_data = \
{'': ['*']}

install_requires = \
['first>=2.0.2,<3.0.0', 'importlib_metadata>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'single-version',
    'version': '1.0',
    'description': 'Small utility to define version string for Poetry-style Python project.',
    'long_description': None,
    'author': 'Nguyễn Hồng Quân',
    'author_email': 'ng.hong.quan@gmail.com',
    'maintainer': 'Nguyễn Hồng Quân',
    'maintainer_email': 'ng.hong.quan@gmail.com',
    'url': 'https://github.com/hongquan/single-version.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
