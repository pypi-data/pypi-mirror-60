# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vega', 'vega.tests']

package_data = \
{'': ['*'], 'vega': ['static/*']}

install_requires = \
['jupyter>=1.0.0,<2.0.0', 'pandas>=0.25.3,<0.26.0']

entry_points = \
{'console_scripts': ['test = pytest:main']}

setup_kwargs = {
    'name': 'vega',
    'version': '3.0.1',
    'description': 'A Jupyter widget for Vega 5 and Vega-Lite 4',
    'long_description': None,
    'author': 'Dominik Moritz',
    'author_email': 'domoritz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
