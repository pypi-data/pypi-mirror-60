# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['couchutils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'couchutils',
    'version': '0.4.0',
    'description': 'A collection of CouchDB utils.',
    'long_description': '# couchutils: Python CouchDB Utils\n\n[![Travis (.org)](https://img.shields.io/travis/rwanyoike/couchutils.svg)](https://travis-ci.org/rwanyoike/couchutils)\n[![Codecov](https://img.shields.io/codecov/c/gh/rwanyoike/couchutils.svg)](https://codecov.io/gh/rwanyoike/couchutils)\n[![GitHub](https://img.shields.io/github/license/rwanyoike/couchutils)](LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/couchutils.svg)](https://pypi.python.org/pypi/couchutils)\n[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n> A collection of CouchDB utils.\n\n## Feature Support\n\n- Support for CouchDB 1.7.x.\n\ncouchutils officially supports **Python 3.6+**.\n\n## Installation\n\nTo install couchutils, simply run:\n\n```shell\n$ pip install -U couchutils\n✨🛋✨\n```\n\n## Documentation\n\nTo use couchutils in a project:\n\n```python\n>>> from couchutils import <UTILS_METHOD>\n```\n\n### Build CouchDB Documents from a Directory\n\n```python\n>>> from couchutils import compile_doc\n>>> compile_doc.compile_docs("<DOC_DIR>")\n{...}\n```\n\nE.g. If passed a directory tree with:\n\n```\n.\n├── example1\n│\xa0\xa0 ├── _id\n│\xa0\xa0 ├── language\n│\xa0\xa0 └── views\n│\xa0\xa0     └── numbers\n│\xa0\xa0         ├── map.js\n│\xa0\xa0         └── reduce\n├── example2\n│\xa0\xa0 └── _id\n└── ignored.txt\n```\n\nThe compiled output would be:\n\n```python\n>>> compile_doc.compile_docs(".")\n{\n    "_design/example1": {"_id": "_design/minimal"},\n    "_design/example2": {\n        "views": {\n            "numbers": {\n                "reduce": "_count",\n                "map": "function (doc) {\\n  if (doc.name) {\\n    emit(doc.name, null);\\n  }\\n}",\n            }\n        },\n        "_id": "_design/basic",\n        "language": "javascript",\n    },\n}\n```\n\nRef: [tests/fixtures/compile_docs](tests/fixtures/compile_docs)\n',
    'author': 'Raymond Wanyoike',
    'author_email': 'raymond.wanyoike@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rwanyoike/couchutils',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
