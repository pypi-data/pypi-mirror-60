# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scripts']

package_data = \
{'': ['*']}

install_requires = \
['fuzzywuzzy>=0.17.0,<0.18.0', 'nltk>=3.4.5,<4.0.0', 'spacy>=2.2.3,<3.0.0']

setup_kwargs = {
    'name': 'phuzzymatcher',
    'version': '0.0.1',
    'description': 'Features the combination of the fuzzywuzzy library and the spacy phrasematcher',
    'long_description': None,
    'author': 'Sebastian Menke',
    'author_email': 'sebastian.menke@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
