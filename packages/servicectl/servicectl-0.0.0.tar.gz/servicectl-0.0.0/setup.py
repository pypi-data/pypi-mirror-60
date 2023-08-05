# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['servicectl']

package_data = \
{'': ['*']}

install_requires = \
['docker>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'servicectl',
    'version': '0.0.0',
    'description': 'Docker stack deployment manager',
    'long_description': "===========================\n Docker Service Controller\n===========================\n\nA simple library for managing Docker stack deployments.\n\nFeatures include:\n\n* Completely atomic stack updates\n* Per container log retrieval\n* Container command execution\n\nIt's meant to be used with `deploy-webhook`_\n\n.. _`deploy-webhook`: https://github.com/TheEdgeOfRage/deploy-webhook/\n",
    'author': 'Pavle Portic',
    'author_email': 'pavle.portic@tilda.center',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheEdgeOfRage/servicectl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
