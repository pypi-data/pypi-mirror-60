# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hn_pwa_api']

package_data = \
{'': ['*']}

install_requires = \
['requests==2.22.0']

setup_kwargs = {
    'name': 'hn-pwa-api',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'flomk',
    'author_email': 'sudogitrekt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
