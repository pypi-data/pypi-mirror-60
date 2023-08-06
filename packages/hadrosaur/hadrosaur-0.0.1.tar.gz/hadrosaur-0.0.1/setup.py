# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hadrosaur']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hadrosaur',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Jay R Bolton',
    'author_email': 'jayrbolton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
