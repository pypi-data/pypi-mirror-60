# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reformat_gherkin', 'reformat_gherkin.ast_node']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.2,<20.0',
 'cattrs>=1.0.0,<2.0.0',
 'click>=7.0,<8.0',
 'gherkin-official>=4.1,<5.0',
 'pyyaml>=5.1,<6.0',
 'wcwidth>=0.1.7,<0.2.0']

entry_points = \
{'console_scripts': ['reformat-gherkin = reformat_gherkin.cli:main']}

setup_kwargs = {
    'name': 'reformat-gherkin',
    'version': '1.1.0',
    'description': 'Formatter for Gherkin language',
    'long_description': "# Reformat-gherkin\n\n[![Build Status](https://dev.azure.com/alephvn/reformat-gherkin/_apis/build/status/ducminh-phan.reformat-gherkin?branchName=master)](https://dev.azure.com/alephvn/reformat-gherkin/_build/latest?definitionId=1&branchName=master) &nbsp; [![Build Status](https://travis-ci.com/ducminh-phan/reformat-gherkin.svg?branch=master)](https://travis-ci.com/ducminh-phan/reformat-gherkin) &nbsp; [![Coverage Status](https://coveralls.io/repos/github/ducminh-phan/reformat-gherkin/badge.svg?branch=master)](https://coveralls.io/github/ducminh-phan/reformat-gherkin?branch=master)\n\n[![Maintainability](https://api.codeclimate.com/v1/badges/16718a231901c293215d/maintainability)](https://codeclimate.com/github/ducminh-phan/reformat-gherkin/maintainability) &nbsp; [![Codacy Badge](https://api.codacy.com/project/badge/Grade/e675ca51b6ac436a980facbcf04b8e5a)](https://www.codacy.com/app/ducminh-phan/reformat-gherkin)\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &nbsp; [![PyPI](https://img.shields.io/pypi/v/reformat-gherkin.svg)](https://pypi.org/project/reformat-gherkin/) &nbsp; [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n\n## Table of Contents\n\n- [About](#about)\n- [Getting Started](#getting-started)\n- [Usage](#usage)\n- [Pre-commit hook](#pre-commit-hook)\n- [Acknowledgements](#acknowledgements)\n\n## About\n\nThis tool is a formatter for Gherkin files. It ensures consistent look regardless of the project and authors.\n\n`reformat-gherkin` can be used either as a command-line tool, or a `pre-commit` hook.\n\n## Getting Started\n\nThese instructions will get you a copy of the project up and running on your local machine for development and testing purposes.\n\n### Prerequisites\n\n- [Python 3.6+](https://www.python.org/downloads/)\n- [Poetry](https://poetry.eustace.io/)\n\n### Installing\n\n1. Clone this repository\n\n   ```bash\n   git clone https://github.com/ducminh-phan/reformat-gherkin.git\n   ```\n\n2. Install dependencies\n\n   ```bash\n   cd reformat-gherkin\n   poetry install\n   ```\n\n3. Install `pre-commit` hooks (if you want to contribute)\n\n   ```bash\n   pre-commit install\n   ```\n\n## Usage\n\n```text\nUsage: reformat-gherkin [OPTIONS] [SRC]...\n\n  Reformat the given Gherkin files and all files in the given directories\n  recursively.\n\nOptions:\n  --check                         Don't write the files back, just return the\n                                  status. Return code 0 means nothing would\n                                  change. Return code 1 means some files would\n                                  be reformatted. Return code 123 means there\n                                  was an internal error.\n  -a, --alignment [left|right]    Specify the alignment of step keywords\n                                  (Given, When, Then,...). If specified, all\n                                  statements after step keywords are left-\n                                  aligned, spaces are inserted before/after\n                                  the keywords to right/left align them. By\n                                  default, step keywords are left-aligned, and\n                                  there is a single space between the step\n                                  keyword and the statement.\n  -n, --newline [LF|CRLF]         Specify the line separators when formatting\n                                  files inplace. If not specified, line\n                                  separators are preserved.\n  --fast / --safe                 If --fast given, skip the sanity checks of\n                                  file contents. [default: --safe]\n  --single-line-tags / --multi-line-tags\n                                  If --single-line-tags given, output\n                                  consecutive tags on one line. If --multi-\n                                  line-tags given, output one tag per line.\n                                  [default: --multi-line-tags]\n  --config FILE                   Read configuration from FILE.\n  --version                       Show the version and exit.\n  --help                          Show this message and exit.\n```\n\n### Config file\n\nThe tool is able to read project-specific default values for its command line options from a `.reformat-gherkin.yaml` file.\n\nBy default, `reformat-gherkin` looks for the config file starting from the common base directory of all files and directories passed on the command line. If it's not there, it looks in parent directories. It stops looking when it finds the file, or a .git directory, or a .hg directory, or the root of the file system, whichever comes first.\n\nExample config file\n\n```yaml\ncheck: False\nalignment: left\n```\n\n## Pre-commit hook\n\nOnce you have installed [pre-commit](https://pre-commit.com/), add this to the `.pre-commit-config.yaml` in your repository:\n\n```text\nrepos:\n  - repo: https://github.com/ducminh-phan/reformat-gherkin\n    rev: stable\n    hooks:\n      - id: reformat-gherkin\n```\n\nThen run `pre-commit install` and you're ready to go.\n\n## Acknowledgements\n\nThis project is inspired by [black](https://github.com/psf/black). Some functions are taken from `black`'s source code.\n",
    'author': 'Duc-Minh Phan',
    'author_email': 'alephvn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ducminh-phan/reformat-gherkin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
