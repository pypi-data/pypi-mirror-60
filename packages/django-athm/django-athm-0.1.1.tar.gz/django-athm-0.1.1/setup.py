# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_athm',
 'django_athm.management',
 'django_athm.management.commands',
 'django_athm.migrations',
 'django_athm.templatetags']

package_data = \
{'': ['*'], 'django_athm': ['templates/*']}

install_requires = \
['django<3', 'httpx>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'django-athm',
    'version': '0.1.1',
    'description': 'Django + ATH Móvil',
    'long_description': None,
    'author': 'Raúl Negrón',
    'author_email': 'raul.esteban.negron@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
