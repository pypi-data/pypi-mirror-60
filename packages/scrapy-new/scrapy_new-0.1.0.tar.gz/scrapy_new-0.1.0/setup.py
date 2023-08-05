# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scrapy_new']

package_data = \
{'': ['*'], 'scrapy_new': ['templates/*']}

install_requires = \
['inflection>=0.3.1,<0.4.0', 'mako>=1.1.1,<2.0.0', 'scrapy>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'scrapy-new',
    'version': '0.1.0',
    'description': 'A package providing code generation command for scrapy CLI',
    'long_description': None,
    'author': 'Kristobal Junta',
    'author_email': 'junta.kristobal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
