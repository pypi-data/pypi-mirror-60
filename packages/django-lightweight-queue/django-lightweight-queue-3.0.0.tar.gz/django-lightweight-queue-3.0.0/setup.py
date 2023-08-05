# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_lightweight_queue',
 'django_lightweight_queue.backends',
 'django_lightweight_queue.management',
 'django_lightweight_queue.management.commands',
 'django_lightweight_queue.middleware']

package_data = \
{'': ['*']}

install_requires = \
['daemonize>=2.5.0,<2.6.0',
 'django>=1.11.27,<3.0',
 'prometheus-client>=0.7,<1.0']

extras_require = \
{'redis': ['redis']}

setup_kwargs = {
    'name': 'django-lightweight-queue',
    'version': '3.0.0',
    'description': 'Lightweight & modular queue and cron system for Django',
    'long_description': None,
    'author': 'Thread Engineering',
    'author_email': 'tech@thread.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
