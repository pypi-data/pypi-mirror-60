# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['buildahscript']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['buildahscript-py = buildahscript.cli:main']}

setup_kwargs = {
    'name': 'buildahscript',
    'version': '0.1.0',
    'description': 'Tool for buildah scripts',
    'long_description': None,
    'author': 'Jamie Bliss',
    'author_email': 'jamie@ivyleav.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
