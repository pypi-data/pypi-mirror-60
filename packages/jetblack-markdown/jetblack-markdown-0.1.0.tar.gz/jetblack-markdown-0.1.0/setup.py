# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jetblack_markdown', 'jetblack_markdown.metadata']

package_data = \
{'': ['*'], 'jetblack_markdown': ['templates/*']}

install_requires = \
['docstring-parser>=0.6,<0.7', 'markdown>=3.1,<4.0']

setup_kwargs = {
    'name': 'jetblack-markdown',
    'version': '0.1.0',
    'description': 'A markdown extension for python documentation',
    'long_description': '# jetblack-markdown\n\nMarkdown extensions for automatic document generation.\n\nSee [here](https://rob-blackbourn.github.io/jetblack-markdown/) for documentation.\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/jetblack-markdown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
