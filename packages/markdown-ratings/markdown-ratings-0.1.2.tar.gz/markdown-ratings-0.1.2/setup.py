# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markdown_ratings']

package_data = \
{'': ['*']}

install_requires = \
['markdown>=3.1.1,<4.0.0']

setup_kwargs = {
    'name': 'markdown-ratings',
    'version': '0.1.2',
    'description': 'A Markdown plugin to show star ratings on your page.',
    'long_description': None,
    'author': 'Johan Vergeer',
    'author_email': 'johanvergeer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
