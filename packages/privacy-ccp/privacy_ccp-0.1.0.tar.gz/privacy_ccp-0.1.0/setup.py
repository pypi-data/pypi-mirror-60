# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['privacy_ccp',
 'privacy_ccp.communication_system',
 'privacy_ccp.crypto',
 'privacy_ccp.privacy_contracts',
 'privacy_ccp.simulation_environment']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.9.4,<4.0.0']

entry_points = \
{'console_scripts': ['init = test_simulation:main']}

setup_kwargs = {
    'name': 'privacy-ccp',
    'version': '0.1.0',
    'description': 'Privacy Preserving Collective Computation Platform',
    'long_description': None,
    'author': 'Pradipta Deb',
    'author_email': 'pradipta.deb@inria.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
