# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_terminal_notifier']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-terminal-notifier',
    'version': '0.1.1',
    'description': 'A python wrapper for terminal-notifier',
    'long_description': None,
    'author': 'flomk',
    'author_email': 'sudogitrekt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
