# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkdocs_apidoc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mkdocs-apidoc',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Evan',
    'author_email': 'ecurtin2@illinois.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
