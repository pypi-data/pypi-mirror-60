# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dj_pony',
 'dj_pony.tenant',
 'dj_pony.tenant.drf',
 'dj_pony.tenant.helpers',
 'dj_pony.tenant.management',
 'dj_pony.tenant.management.commands',
 'dj_pony.tenant.migrations',
 'dj_pony.tenant.polymorphic',
 'dj_pony.tenant.retrievers',
 'dj_pony.tenant.tools']

package_data = \
{'': ['*']}

install_requires = \
['deprecated>=1.2.7,<2.0.0',
 'dj-pony.ulidfield>=0.3.1,<0.4.0',
 'django-jsonfield>=1.3.1,<2.0.0',
 'django-model-utils>=3.2.0,<4.0.0',
 'django>=2.2.6,<3.0.0',
 'packaging>=19.0,<20.0',
 'sentinels>=1.0.0,<2.0.0']

extras_require = \
{'polymorphic': ['django-polymorphic>=2.1.2,<3.0.0']}

setup_kwargs = {
    'name': 'dj-pony.tenant',
    'version': '0.10.2',
    'description': 'A Shared Schema based Multi-Tenancy Library for Django.',
    'long_description': None,
    'author': 'Samuel Bishop',
    'author_email': 'sam@techdragon.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dj-pony-pro/dj-pony-tenant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
