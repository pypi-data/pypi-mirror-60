# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hostwinds', 'hostwinds.entry']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22.0,<3.0.0']

entry_points = \
{'console_scripts': ['hw-alert = hostwinds.entry.alert_command:main']}

setup_kwargs = {
    'name': 'hostwinds-tool',
    'version': '1.0.0',
    'description': 'A hostwinds api toolset.',
    'long_description': None,
    'author': 'Ray',
    'author_email': 'linxray@gmail.com',
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
