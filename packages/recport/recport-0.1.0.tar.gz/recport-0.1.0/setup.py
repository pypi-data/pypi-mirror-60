# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['recport']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['recport = recport.main:run1',
                     'showport = recport.main:run2']}

setup_kwargs = {
    'name': 'recport',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'harit',
    'author_email': 'harit.c@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
