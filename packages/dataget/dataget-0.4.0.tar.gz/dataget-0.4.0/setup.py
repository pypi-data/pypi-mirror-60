# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataget', 'dataget.vision']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles',
 'httpx',
 'idx2numpy',
 'kaggle>=1.5.6,<2.0.0',
 'numpy',
 'pandas',
 'pyarrow',
 'tqdm']

setup_kwargs = {
    'name': 'dataget',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Cristian Garcia',
    'author_email': 'cgarcia.e88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.7.6',
}


setup(**setup_kwargs)
