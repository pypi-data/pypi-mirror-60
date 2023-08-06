# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vvtool', 'vvtool.migrations', 'vvtool.migrations.data']

package_data = \
{'': ['*']}

install_requires = \
['alley==0.0.3',
 'attrs',
 'click>=6.0,<7.0',
 'importlib_resources==1.0',
 'mongoengine==0.18.2',
 'pylint==2.3',
 'pymongo==3.8']

entry_points = \
{'console_scripts': ['vvtool = vvtool.cli:cli']}

setup_kwargs = {
    'name': 'voteview-dev',
    'version': '0.1.5',
    'description': 'Voteview command-line interface',
    'long_description': "========\nvvtool\n========\n\n.. start-badges\n\n.. list-table::\n    :stub-columns: 1\n\n    * - docs\n      - |docs|\n    * - tests\n      - | |travis|\n        |\n    * - package\n      - | |version| |wheel| |supported-versions| |supported-implementations|\n        | |commits-since|\n\n.. |docs| image:: https://readthedocs.org/projects/voteview-dev/badge/?style=flat\n    :target: https://readthedocs.org/projects/voteview-dev\n    :alt: Documentation Status\n\n\n.. |travis| image:: https://img.shields.io/travis/com/voteview/voteview-dev/master\n    :alt: Travis-CI Build Status\n    :target: https://travis-ci.com/voteview/voteview-dev\n\n.. |version| image:: https://img.shields.io/pypi/v/voteview-dev.svg\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/project/voteview-dev\n\n.. |commits-since| image:: https://img.shields.io/github/commits-since/voteview/voteview-dev/v0.1.5.svg\n    :alt: Commits since latest release\n    :target: https://github.com/voteview/voteview-dev/compare/v0.1.5...master\n\n.. |wheel| image:: https://img.shields.io/pypi/wheel/voteview-dev.svg\n    :alt: PyPI Wheel\n    :target: https://pypi.org/project/voteview-dev\n\n.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/voteview-dev.svg\n    :alt: Supported versions\n    :target: https://pypi.org/project/voteview-dev\n\n.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/voteview-dev.svg\n    :alt: Supported implementations\n    :target: https://pypi.org/project/voteview-dev\n\n\n.. end-badges\n\nThis project contains tools for managing the Voteview server.\n\n\nAny manual changes to the database contents can be applied through this tool.\n\n\nWhat's good\n-------------\n\nThe advantages of using ``vvtool``:\n\n- All migrations are versioned.\n- All migrations can be programatically applied and reverted.\n- All migrations are documented in the changelog.\n- All migrations can be developed and tested on the user's local computer instead of running\n  for the first time in production.\n- The representation of database objects can be standardized: vvtool defines a set of\n  attributes for ``Member``, ``Rollcall``, and other objects.\n- Any changes to software or migrations can be tested automatically on a `continuous\n  integration server`_.\n- The software can be `documented centrally <docs>`_ instead of using scattered shell scripts.\n- ``vvtool`` connects directly to a test database or the production database,\n  reducing the differences between the test environment and the production environment.\n\n\nWhat's bad\n-----------\n\n- Requires a few setup steps.\n- Doesn't **require** changes to go through continuous integration testing, since users\n  can submit jobs directly to the target server. So it's possible that a script could be\n  executed without ever being tested. This shortcoming could be changed by swiching to a\n  continuous **deployment** strategy whereby users would simply submit migrations to\n  GitHub, wait for them to go through testing, and then the migrations would be\n  automatically applied to the production database. The current situation is much simpler,\n  so I've stuck with that for now.\n\nDocumentation\n=============\n\nhttps://voteview-dev.readthedocs.io/\n\n\n\n.. _continuous integration server: https://travis-ci.com/voteview/voteview-dev\n.. _docs: https://voteview-dev.readthedocs.io/\n",
    'author': 'Adam Boche',
    'author_email': 'aboche@ucla.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
