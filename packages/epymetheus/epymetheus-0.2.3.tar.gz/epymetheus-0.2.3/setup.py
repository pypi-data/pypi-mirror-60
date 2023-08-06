# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['epymetheus',
 'epymetheus.datasets',
 'epymetheus.helper',
 'epymetheus.pipe',
 'epymetheus.utils']

package_data = \
{'': ['*']}

install_requires = \
['pandas-datareader>=0.8.1,<0.9.0',
 'pandas>=0.25.3,<0.26.0',
 'pyyaml>=5.3,<6.0']

setup_kwargs = {
    'name': 'epymetheus',
    'version': '0.2.3',
    'description': 'Python framework for multi-asset backtesting.',
    'long_description': None,
    'author': 'Shota Imaki',
    'author_email': 'shota.imaki@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
