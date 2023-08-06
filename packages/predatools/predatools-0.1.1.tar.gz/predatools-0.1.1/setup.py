# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['predatools']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.11.9,<2.0.0',
 'fastavro>=0.22.9,<0.23.0',
 'pandas>=1.0.0,<2.0.0',
 'pyarrow>=0.15.1,<0.16.0',
 's3fs>=0.4.0,<0.5.0',
 'tqdm>=4.42.0,<5.0.0']

setup_kwargs = {
    'name': 'predatools',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Kawin Liaowongphuthorn',
    'author_email': 'liaokangtai@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
