# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypdns']

package_data = \
{'': ['*']}

install_requires = \
['requests-cache>=0.5.2,<0.6.0']

setup_kwargs = {
    'name': 'pypdns',
    'version': '1.5',
    'description': 'Python API for PDNS.',
    'long_description': None,
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CIRCL/PyPDNS',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
