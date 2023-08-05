# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['equium']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'equium',
    'version': '0.0.1',
    'description': 'Experimenting with Equality',
    'long_description': "# Experimenting with Equality\n\n\n**Don't use this package!**\n\n**It will change out from under you**\n\n```\npoetry run python -m unittest discover -s tests\n```\n",
    'author': 'John Paulett',
    'author_email': 'john@paulett.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
