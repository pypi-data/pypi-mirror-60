# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tabler', 'tabler.tabletypes', 'tabler.tohtml']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.11.0,<3.0.0',
 'openpyxl>=3.0.3,<4.0.0',
 'pyexcel-ods>=0.5.6,<0.6.0',
 'requests>=2.22.0,<3.0.0',
 'urllib3>=1.25.8,<2.0.0']

setup_kwargs = {
    'name': 'tabler',
    'version': '2.4.0',
    'description': 'Simple interface for tabulated data and .csv files',
    'long_description': "===============================================\nTabler - Simple interaction with tabulated data\n===============================================\n\n.. image:: https://travis-ci.org/lukeshiner/tabler.svg?branch=master\n    :target: https://travis-ci.org/lukeshiner/tabler\n\n.. image:: https://readthedocs.org/projects/tabler/badge/?version=latest\n    :target: https://tabler.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://badge.fury.io/py/tabler.svg\n    :target: https://pypi.org/project/tabler/\n\n.. image:: https://pypip.in/py_versions/tabler/badge.svg\n    :target: https://pypi.org/project/tabler/\n\n\nWhat is tabler?\n===============\n\nTabler allows you to quickly and easily open, edit, create and update common\nfiles that hold data in a tabulated format, such as CSV or XLSX files. It's\nsimple API keeps your source code clean and allows easy use of an interactive\nsession.\n\nIt can:\n    + Access spreadsheet files.\n    + Update text in cells.\n    + Write spreadsheet files.\n\nCompatible formats:\n    + .csv\n    + Open Spreadsheet Format .ods\n    + Microsoft Excel .xlsx\n    + HTML (Write only)\n\nIf you need another format, see the documentation_ for how\nto add your own.\n\nThe full documentation is available on `Read the Docs\n<https://tabler.readthedocs.io/en/latest/>`_.\n\nTabler lives on GitHub_.\n\n.. _documentation: https://tabler.readthedocs.io/en/latest/\n.. _GitHub: https://github.com/lukeshiner/tabler.git\n\nContact\n_______\n\nPlease send all comments and queries to Luke Shiner at luke@lukeshiner.com\nIssues can be reported on GitHub_\n\nLicense\n_______\n\nDistributed with MIT License.\n\nCredits\n_______\n\nCreated by Luke Shiner (luke@lukeshiner.com)\n",
    'author': 'Luke Shiner',
    'author_email': 'luke@lukeshiner.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lukeshiner/tabler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
