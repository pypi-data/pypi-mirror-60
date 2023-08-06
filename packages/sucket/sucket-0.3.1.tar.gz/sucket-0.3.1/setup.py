# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sucket']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore>=0.11.1,<0.12.0',
 'click>=7.0,<8.0',
 'typing_extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['sucket = sucket:sucket']}

setup_kwargs = {
    'name': 'sucket',
    'version': '0.3.1',
    'description': 'A tool to get all files from an S3 bucket',
    'long_description': None,
    'author': 'Axel',
    'author_email': 'sucket@absalon.is',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
