# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mulatu']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mulatu',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Hadrien David',
    'author_email': 'hadrien@ectobal.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
