# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ylib']

package_data = \
{'': ['*']}

install_requires = \
['autopep8>=1.5,<2.0',
 'flake8>=3.7.9,<4.0.0',
 'invoke>=1.4.0,<2.0.0',
 'ipython>=7.11.1,<8.0.0',
 'isort>=4.3.21,<5.0.0',
 'prettytable>=0.7.2,<0.8.0',
 'py-term>=0.6,<0.7',
 'pytest-cov>=2.8.1,<3.0.0',
 'toml>=0.10.0,<0.11.0',
 'tqdm>=4.41.1,<5.0.0']

setup_kwargs = {
    'name': 'ylib',
    'version': '0.1.0',
    'description': 'My Library',
    'long_description': None,
    'author': 'yassu',
    'author_email': 'mathyassu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
