# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['srusp']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=4.0,<5.0',
 'numpy>=1.18.1,<2.0.0',
 'pandas>=0.25.3,<0.26.0',
 'scikit-learn>=0.22.1,<0.23.0',
 'scipy>=1.4.1,<2.0.0',
 'xarray>=0.14.1,<0.15.0']

setup_kwargs = {
    'name': 'srusp',
    'version': '0.1.0',
    'description': 'Python package for the SRUSP method',
    'long_description': None,
    'author': 'Akio Taniguchi',
    'author_email': 'taniguchi@a.phys.nagoya-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
