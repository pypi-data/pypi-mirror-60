# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['keios_dynabuffers_knowr', 'keios_dynabuffers_knowr.semantic_search']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'keios-dynabuffers-knowr',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'devs',
    'author_email': 'devs@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
