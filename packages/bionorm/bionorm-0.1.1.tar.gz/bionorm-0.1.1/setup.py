# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bionorm']

package_data = \
{'': ['*'], 'bionorm': ['templates/*']}

install_requires = \
['biopython>=1.76,<2.0',
 'click>=7.0,<8.0',
 'click_plugins>=1.1.1,<2.0.0',
 'coverage>=5.0.3,<6.0.0',
 'importlib_metadata>=1.5.0,<2.0.0',
 'ruamel.yaml>=0.16.6,<0.17.0',
 'sequencetools>=0.0.5,<0.0.6']

entry_points = \
{'console_scripts': ['bionorm = bionorm:cli']}

setup_kwargs = {
    'name': 'bionorm',
    'version': '0.1.1',
    'description': 'normalize and verify genomic data',
    'long_description': 'bionorm\n======\ncreating, searching, and analyzing phylogenetic signatures from genomes or reads of DNA.\n\nPrerequisites\n-------------\nPython 3.6 or greater is required.\n\nRun-time dependencies of bionorm are : ::\n\n    biopython, click, ruamel.yaml, and sequencetools.\n\nbionorm uses the poetry dependency manager\n\nInstallation\n------------\nThis package is tested under Linux and MacOS using Python 3.7.\ninstall via pip (or pip3 under some distributions) : ::\n\n     pip install bionorm\n\nIf you wish to develop bionorm,  download a `release <https://github.com/ncgr/bionorm/releases>`_\nand in the top-level directory: ::\n\n\tpip install --editable .\n\nIf you wish to have pip install directly from git, use this command: ::\n\n\tpip install git+https://github.com/ncgr/bionorm.git\n\n\nUsage\n-----\nInstallation puts a single script called ``bionorm`` in your path.  The usage format is::\n\n    bionorm [GLOBALOPTIONS] COMMAND [COMMANDOPTIONS] [ARGS]\n\nA listing of commands is available via ``bionorm --help``.  Current available commands are:\n\n============================= ====================================================\n  busco                       Perform BUSCO checks.\n  detector                    Detect/correct incongruencies among files.\n  fasta                       Check for GFF/FASTA consistency.\n  generate_readme             Generates a README file with details of genome.\n  index                       Indexes FASTA file.\n\n============================= ====================================================\n\n\n+-------------------+------------+------------+\n| Latest Release    | |pypi|     | |bionorm|  |\n+-------------------+------------+            +\n| GitHub            | |repo|     |            |\n+-------------------+------------+            +\n| License           | |license|  |            |\n+-------------------+------------+            +\n| Documentation     | |rtd|      |            |\n+-------------------+------------+            +\n| Travis Build      | |travis|   |            |\n+-------------------+------------+            +\n| Coverage          | |coverage| |            |\n+-------------------+------------+            +\n| Code Grade        | |codacy|   |            |\n+-------------------+------------+            +\n| Dependencies      | |depend|   |            |\n+-------------------+------------+            +\n| Issues            | |issues|   |            |\n+-------------------+------------+------------+\n\n\n.. |bionorm| image:: docs/normal.jpg\n     :alt: Make me NORMAL, please!\n\n.. |pypi| image:: https://img.shields.io/pypi/v/bionorm.svg\n    :target: https://pypi.python.org/pypi/bionorm\n    :alt: Python package\n\n.. |repo| image:: https://img.shields.io/github/commits-since/ncgr/bionorm/0.1.svg\n    :target: https://github.com/ncgr/bionorm\n    :alt: GitHub repository\n\n.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/ncgr/bionorm/blob/master/LICENSE.txt\n    :alt: License terms\n\n.. |rtd| image:: https://readthedocs.org/projects/bionorm/badge/?version=latest\n    :target: http://bionorm.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Server\n\n.. |travis| image:: https://img.shields.io/travis/ncgr/bionorm.svg\n    :target:  https://travis-ci.org/ncgr/bionorm\n    :alt: Travis CI\n\n.. |codacy| image:: https://api.codacy.com/project/badge/Grade/b23fc0c167fc4660bb649320e14dac7f\n    :target: https://www.codacy.com/gh/ncgr/bionorm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ncgr/bionorm&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n\n.. |coverage| image:: https://codecov.io/gh/ncgr/bionorm/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/ncgr/bionorm\n    :alt: Codecov.io test coverage\n\n.. |issues| image:: https://img.shields.io/github/issues/ncgr/bionorm.svg\n    :target:  https://github.com/ncgr/bionorm/issues\n    :alt: Issues reported\n\n.. |depend| image:: https://api.dependabot.com/badges/status?host=github&repo=ncgr/bionorm\n     :target:https://app.dependabot.com/accounts/ncgr/repos/236847525\n     :alt: dependabot dependencies\n\n',
    'author': 'Connor Cameron',
    'author_email': 'ctc@ncgr.org',
    'maintainer': 'Joel Berendzen',
    'maintainer_email': 'joelb@ncgr.org',
    'url': 'https://github.com/ncgr/ncgr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
