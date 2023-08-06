# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_publish', 'poetry_publish.tests', 'poetry_publish.utils']

package_data = \
{'': ['*']}

install_requires = \
['python-creole>=1.4.2,<2.0.0']

entry_points = \
{'console_scripts': ['publish = poetry_publish.self:publish_poetry_publish',
                     'update_rst_readme = '
                     'poetry_publish.self:update_poetry_publish_readme']}

setup_kwargs = {
    'name': 'poetry-publish',
    'version': '0.2.0',
    'description': 'Helper to build and upload a project that used poetry to PyPi, with prechecks',
    'long_description': None,
    'author': 'JensDiemer',
    'author_email': 'git@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
