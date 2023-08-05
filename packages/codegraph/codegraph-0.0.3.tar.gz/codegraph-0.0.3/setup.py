# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codegraph']

package_data = \
{'': ['*'], 'codegraph': ['conf/*', 'docs/img/*']}

install_requires = \
['clifier>=0.0.3,<0.0.4', 'matplotlib>=3.1,<4.0', 'networkx>=2.4,<3.0']

entry_points = \
{'console_scripts': ['cg = codegraph.main:cli']}

setup_kwargs = {
    'name': 'codegraph',
    'version': '0.0.3',
    'description': 'Tool that create a graph of code to show dependencies between code entities (methods, classes and etc).',
    'long_description': None,
    'author': 'xnuinside',
    'author_email': 'xnuinside@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
