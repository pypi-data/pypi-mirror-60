# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libs', 'libs.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'libs',
    'version': '0.0.3',
    'description': 'Packages of tools',
    'long_description': None,
    'author': 'phyng',
    'author_email': 'phyngk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
