# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dspg']

package_data = \
{'': ['*']}

install_requires = \
['pyyaml>=5.3,<6.0', 'wikidata>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['dspg = dspg.cli:main']}

setup_kwargs = {
    'name': 'dspg',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Dominic Looser',
    'author_email': 'dominic.looser@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
