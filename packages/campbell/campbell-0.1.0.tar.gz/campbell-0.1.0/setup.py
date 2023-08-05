# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['campbell']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'campbell',
    'version': '0.1.0',
    'description': 'Dataframe visualization on jupyter',
    'long_description': None,
    'author': 'horoiwa',
    'author_email': 'horoiwa195@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
