# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multi_dash', 'multi_dash.index']

package_data = \
{'': ['*'], 'multi_dash.index': ['templates/multi_dash/*']}

setup_kwargs = {
    'name': 'multi-dash',
    'version': '0.2.0',
    'description': 'A light framework to make multi-page dash based apps.',
    'long_description': None,
    'author': 'James Saunders',
    'author_email': 'james@businessoptics.biz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
