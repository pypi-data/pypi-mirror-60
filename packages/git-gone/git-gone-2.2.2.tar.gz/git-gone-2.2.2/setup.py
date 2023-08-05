# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_gone']

package_data = \
{'': ['*']}

install_requires = \
['plumbum>=1.6.8,<2.0.0']

entry_points = \
{'console_scripts': ['git-gone = git_gone.__main__:main']}

setup_kwargs = {
    'name': 'git-gone',
    'version': '2.2.2',
    'description': 'A simple tool to track visited Git repositories, and check them for unpushed/committed changes',
    'long_description': None,
    'author': 'Angus Hollands',
    'author_email': 'goosey15@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/agoose77/git-gone',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
