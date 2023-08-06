# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reasonable']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'reasonable',
    'version': '0.1.0',
    'description': "Python interface to 'reasonable', a Datalog implementation of the OWL 2 RL profile",
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
