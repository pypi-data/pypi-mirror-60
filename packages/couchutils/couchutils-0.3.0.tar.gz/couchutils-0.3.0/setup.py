# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['couchutils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'couchutils',
    'version': '0.3.0',
    'description': 'A collection of CouchDB utils.',
    'long_description': None,
    'author': 'Raymond Wanyoike',
    'author_email': 'raymond.wanyoike@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
