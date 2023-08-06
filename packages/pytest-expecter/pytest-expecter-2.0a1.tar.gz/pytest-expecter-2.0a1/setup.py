# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['expecter']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pytest-expecter = expecter.plugin']}

setup_kwargs = {
    'name': 'pytest-expecter',
    'version': '2.0a1',
    'description': 'Better testing with expecter and pytest.',
    'long_description': '# Overview\n\nA `pytest` plugin based on [garybernhardt/expecter](https://github.com/garybernhardt/expecter) that hides the internal stacktrace.\n\n[![Build Status](http://img.shields.io/travis/jacebrowning/pytest-expecter/plugin.svg)](https://travis-ci.org/jacebrowning/pytest-expecter)\n[![PyPI Version](http://img.shields.io/pypi/v/pytest-expecter.svg)](https://pypi.python.org/pypi/pytest-expecter)\n\n# Quick Start\n\nThis lets you write tests (optionally using [ropez/pytest-describe](https://github.com/ropez/pytest-describe)) like this:\n\n```python\ndef describe_foobar():\n\n    def it_can_pass(expect):\n        expect(2 + 3) == 5\n\n    def it_can_fail(expect):\n        expect(2 + 3) == 6\n```\n\nand get output like this:\n\n```text\n============================= FAILURES =============================\n___________________ describe_foobar.it_can_fail ____________________\n\n    def it_can_fail(expect):\n>       expect(2 + 3) == 6\nE       AssertionError: Expected 6 but got 5\n\ntest_foobar.py:7: AssertionError\n================ 1 failed, 1 passed in 2.67 seconds ================\n```\n\n# Installation\n\nInstall it directly into an activated virtual environment:\n\n```\n$ pip install pytest-expecter\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```\n$ poetry add pytest-expecter\n```\n\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/pytest-expecter/demo',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
