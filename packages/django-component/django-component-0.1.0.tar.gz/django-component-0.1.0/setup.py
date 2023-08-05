# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_component']

package_data = \
{'': ['*']}

install_requires = \
['django>=1.11']

setup_kwargs = {
    'name': 'django-component',
    'version': '0.1.0',
    'description': 'Django template tags to create composable components',
    'long_description': None,
    'author': 'Jérôme Bon',
    'author_email': 'bon.jerome@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
