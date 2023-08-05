# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sudosearch']

package_data = \
{'': ['*']}

install_requires = \
['spacy==2.2.3']

setup_kwargs = {
    'name': 'sudosearch',
    'version': '0.3.0',
    'description': 'Google Crawler and Keyword Checker',
    'long_description': None,
    'author': 'John Aldrich Bernardo',
    'author_email': '4ldrich@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
