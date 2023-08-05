# couchutils: Python CouchDB Utils

[![Travis (.org)](https://img.shields.io/travis/rwanyoike/couchutils.svg)](https://travis-ci.org/rwanyoike/couchutils)
[![Codecov](https://img.shields.io/codecov/c/gh/rwanyoike/couchutils.svg)](https://codecov.io/gh/rwanyoike/couchutils)
[![GitHub](https://img.shields.io/github/license/rwanyoike/couchutils)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/couchutils.svg)](https://pypi.python.org/pypi/couchutils)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A collection of CouchDB utils.

## Feature Support

- Support for CouchDB 1.7.x.

couchutils officially supports **Python 3.6+**.

## Installation

To install couchutils, simply run:

```shell
$ pip install -U couchutils
✨🛋✨
```

## Documentation

To use couchutils in a project:

```python
>>> from couchutils import <UTILS_METHOD>
```

### Build CouchDB Documents from a Directory

```python
>>> from couchutils import compile_doc
>>> compile_doc.compile_docs("<DOC_DIR>")
{...}
```

E.g. If passed a directory tree with:

```
.
├── example1
│   ├── _id
│   ├── language
│   └── views
│       └── numbers
│           ├── map.js
│           └── reduce
├── example2
│   └── _id
└── ignored.txt
```

The compiled output would be:

```python
>>> compile_doc.compile_docs(".")
{
    "_design/example1": {"_id": "_design/minimal"},
    "_design/example2": {
        "views": {
            "numbers": {
                "reduce": "_count",
                "map": "function (doc) {\n  if (doc.name) {\n    emit(doc.name, null);\n  }\n}",
            }
        },
        "_id": "_design/basic",
        "language": "javascript",
    },
}
```

Ref: [tests/fixtures/compile_docs](tests/fixtures/compile_docs)
