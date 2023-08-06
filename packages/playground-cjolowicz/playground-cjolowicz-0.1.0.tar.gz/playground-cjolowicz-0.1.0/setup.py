# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['playground_cjolowicz']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'playground-cjolowicz',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Claudio Jolowicz',
    'author_email': 'claudio.jolowicz@cyren.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
