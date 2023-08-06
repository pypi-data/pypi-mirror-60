# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edelweiss_data']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=0.23.0', 'pyjwt>=1.5.3,<2.0.0', 'requests>=2.18.4,<3.0.0']

setup_kwargs = {
    'name': 'edelweiss-data',
    'version': '0.2.1',
    'description': 'Python client for EdelweissData',
    'long_description': None,
    'author': 'Edelweiss Connect',
    'author_email': 'info@edelweissconnect.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
