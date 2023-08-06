# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['simple_stat_learning']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.1.2,<4.0.0', 'numpy>=1.18.1,<2.0.0', 'seaborn>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'simple-stat-learning',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
