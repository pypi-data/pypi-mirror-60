# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_fahrenheit',
 'django_fahrenheit.migrations',
 'django_fahrenheit.templatetags']

package_data = \
{'': ['*']}

install_requires = \
['django-generic-helpers>=1.0,<2.0', 'geoip2>=2.9,<3.0']

setup_kwargs = {
    'name': 'django-fahrenheit',
    'version': '0.1.3',
    'description': 'A tool for easily restrict access to some project URLs or even objects for legal reasons.',
    'long_description': '#################\ndjango-fahrenheit\n#################\n\nA tool for easily restrict access to some project URLs or even objects for legal reasons.\n\nCurrent software version is **0.1.3**\n',
    'author': 'Mikhail Porokhovnichenko',
    'author_email': 'marazmiki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marazmiki/django-fahrenheit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
