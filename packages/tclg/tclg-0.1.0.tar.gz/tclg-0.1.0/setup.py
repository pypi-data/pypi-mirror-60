# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tclg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tclg',
    'version': '0.1.0',
    'description': 'Utilities, helpers, sugar, etc. for Travis C. LaGrone.',
    'long_description': None,
    'author': 'Travis C. LaGrone',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
