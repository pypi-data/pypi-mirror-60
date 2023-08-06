# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bionorm']

package_data = \
{'': ['*'], 'bionorm': ['templates/*']}

install_requires = \
['biopython>=1.76,<2.0',
 'click>=7.0,<8.0',
 'ruamel.yaml>=0.16.6,<0.17.0',
 'sequencetools>=0.0.5,<0.0.6']

setup_kwargs = {
    'name': 'bionorm',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Joel Berendzen',
    'author_email': 'joel@ncgr.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
