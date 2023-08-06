# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geopatra']

package_data = \
{'': ['*']}

install_requires = \
['folium>=0.10.1,<0.11.0', 'geopandas>=0.6.2,<0.7.0']

setup_kwargs = {
    'name': 'geopatra',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'sangarshanan',
    'author_email': 'sangarshanan1998@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
