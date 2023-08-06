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
    'version': '0.1.2',
    'description': 'Django + ATH Móvil',
    'long_description': '# django-athm \n\n![CI](https://github.com/django-athm/django-athm/workflows/CI/badge.svg?branch=master)\n[![Codecov status](https://codecov.io/gh/django-athm/django-athm/branch/master/graph/badge.svg)](https://codecov.io/gh/django-athm/django-athm)\n[![PyPI version](https://img.shields.io/pypi/v/django-athm.svg)](https://pypi.org/project/django-athm/)\n[![Packaged with Poetry](https://img.shields.io/badge/package_manager-poetry-blue.svg)](https://poetry.eustace.io/)\n![Code style badge](https://badgen.net/badge/code%20style/black/000)\n![License badge](https://img.shields.io/github/license/django-athm/django-athm.svg)\n\nDjango + ATH Móvil\n\n### Documentation\n\nFor information on installation and configuration, see the documentation at:\n\nhttps://django-athm.github.io/django-athm/\n\n## Legal\n\nThis project is not affiliated with or endorsed by [Evertec, Inc.](https://www.evertecinc.com/) or [ATH Móvil](https://portal.athmovil.com/) in any way.\n\n\n## References\n\n- https://github.com/evertec/athmovil-javascript-api\n\n- https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax\n\n- https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/\n\n',
    'author': 'Raúl Negrón',
    'author_email': 'raul.esteban.negron@gmail.com',
    'maintainer': 'Raúl Negrón',
    'maintainer_email': 'raul.esteban.negron@gmail.com',
    'url': 'https://github.com/django-athm/django-athm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
