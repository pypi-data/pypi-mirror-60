# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quantumgraphs']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=7.11,<8.0',
 'matplotlib>=3.1,<4.0',
 'networkx>=1.10,<2.0',
 'numpy>=1.18,<2.0',
 'p-tqdm>=1.3,<2.0',
 'pandas>=0.25,<0.26',
 'scipy>=1.4,<2.0',
 'seaborn>=0.10,<0.11']

setup_kwargs = {
    'name': 'quantumgraphs',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'ziofil',
    'author_email': 'miatto@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
