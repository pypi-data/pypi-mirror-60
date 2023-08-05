# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparkql', 'sparkql.fields']

package_data = \
{'': ['*']}

install_requires = \
['pyspark==2.4.1']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7.0,<0.8.0']}

entry_points = \
{'console_scripts': ['find-releasable-changes = tasks:find_releasable_changes',
                     'lint = tasks:lint',
                     'prepare-release = tasks:prepare_release',
                     'reformat = tasks:reformat',
                     'test = tasks:test',
                     'typecheck = tasks:typecheck',
                     'verify-all = tasks:verify_all']}

setup_kwargs = {
    'name': 'sparkql',
    'version': '0.1.3',
    'description': 'sparkql: Apache Spark SQL DataFrame schema management for sensible humans',
    'long_description': '# sparkql ✨\n\n[![PyPI version](https://badge.fury.io/py/sparkql.svg)](https://badge.fury.io/py/sparkql)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![CircleCI](https://circleci.com/gh/mattjw/sparkql.svg?style=svg)](https://circleci.com/gh/mattjw/sparkql)\n\nPython Spark SQL DataFrame schema management for sensible humans.\n\n## Why use sparkql\n\nsparkql takes the pain out of working with DataFrame schemas in PySpark. It\'s\nparticularly useful when you have structured data.\n\nIn plain old PySpark, you might find that you write schemas like this:\n\n```python\nCITY_SCHEMA = StructType()\nCITY_NAME_FIELD = "name"\nCITY_SCHEMA.add(StructField(CITY_NAME_FIELD, StringType(), False))\nCITY_LAT_FIELD = "latitude"\nCITY_SCHEMA.add(StructField(CITY_LAT_FIELD, FloatType()))\nCITY_LONG_FIELD = "longitude"\nCITY_SCHEMA.add(StructField(CITY_LONG_FIELD, FloatType()))\n\nCONFERENCE_SCHEMA = StructType()\nCONF_NAME_FIELD = "name"\nCONFERENCE_SCHEMA.add(StructField(CONF_NAME_FIELD, StringType(), False))\nCONF_CITY_FIELD = "city"\nCONFERENCE_SCHEMA.add(StructField(CONF_CITY_FIELD, CITY_SCHEMA))\n```\n\nAnd then refer to fields like this:\n\n```python\ndframe.withColumn("city_name", df[CONF_CITY_FIELD][CITY_NAME_FIELD])\n```\n\nWith sparkql, schemas become a lot more literate:\n\n```python\nclass City(Struct):\n    name = String(nullable=False)\n    latitude = Float()\n    longitude = Float()\n\nclass Conference(Struct):\n    name = String(nullable=False)\n    city = City()\n\n# ...create a DataFrame...\n\ndframe.withColumn("city_name", path_col(Conference.city.name))\n```\n\n## Features\n\n### Prettified Spark schema strings\n\nSpark\'s stringified schema representation isn\'t very user friendly, particularly for large schemas:\n\n\n```text\nStructType(List(StructField(name,StringType,false),StructField(city,StructType(List(StructField(name,StringType,false),StructField(latitude,FloatType,true),StructField(longitude,FloatType,true))),true)))\n```\n\nThe function `pretty_schema` will return something more useful:\n\n```text\nStructType(List(\n    StructField(name,StringType,false),\n    StructField(city,\n        StructType(List(\n            StructField(name,StringType,false),\n            StructField(latitude,FloatType,true),\n            StructField(longitude,FloatType,true))),\n        true)))\n```\n\n## Contributing\n\nDevelopers who\'d like to contribute to this project should refer to\n[CONTRIBUTING.md](./CONTRIBUTING.md).\n',
    'author': 'Matt J Williams',
    'author_email': 'mattjw@mattjw.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mattjw/sparkql',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.8,<3.7.0',
}


setup(**setup_kwargs)
