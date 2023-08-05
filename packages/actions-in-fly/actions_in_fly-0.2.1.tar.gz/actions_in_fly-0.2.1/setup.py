# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['actions_in_fly']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.4.0,<4.0.0', 'attrs>=18.2.0,<20.0.0']

entry_points = \
{'console_scripts': ['actions_in_fly = actions_in_fly:main']}

setup_kwargs = {
    'name': 'actions-in-fly',
    'version': '0.2.1',
    'description': 'Test several CI/CD mechanic',
    'long_description': 'Test project\n',
    'author': 'Anton Ilyushenkov',
    'author_email': 'driverx_strogino@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DriverX/actions_in_fly',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
