# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['daculous']

package_data = \
{'': ['*']}

install_requires = \
['graphenelib>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'daculous',
    'version': '0.0.1',
    'description': 'Python library for DACulous',
    'long_description': None,
    'author': 'Fabian Schuh',
    'author_email': 'fabian@chainsquad.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
