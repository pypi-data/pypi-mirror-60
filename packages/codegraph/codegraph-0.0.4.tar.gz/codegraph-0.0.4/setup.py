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
    'version': '0.0.4',
    'description': 'Tool that create a graph of code to show dependencies between code entities (methods, classes and etc).',
    'long_description': 'CodeGraph\n=========\n\nTool that create a graph of code to show dependencies between code entities (methods, classes and etc).\nCodeGraph does not execute code, it is based only on lex and syntax parse, so it not need to install\nall your code dependencies.\n\nUsage:\n\n    pip install codegraph\n\n    cg /path/to/your_python_code\n    # path must be absolute\n\nyour_python_code - module with your python code\n\nFor example, if I put codegraph in my user home directory path will be:\n\n    cg /Users/myuser/codegraph/codegraph\n\nPass \'-o\' flag if you want only print dependencies in console and don\'t want graph visualisation\n\n    cg /path/to/your_python_code -o\n\n\n\n![Code Graph - Code with not used module](/docs/img/code_with_trash_module.png?raw=true "Code with not used module")\n![Code Graph - Code there all modules linked together](/docs/img/normal_code.png?raw=true "Code with modules that linked together")\n\nTODO:\n    1. Create normal readme\n    2. Add tests\n    3. Add possibility to work with any code based (not depend on Python language only)\n    4. Work on visual part of Graph (now it is not very user friendly)\n    5. Add support to variables (names) as entities\n\nContributing:\n    Open PR with improvements that you want to add\n\n    If you have any questions - write me xnuinside@gmail.com',
    'author': 'xnuinside',
    'author_email': 'xnuinside@gmail.com',
    'url': 'https://github.com/xnuinside/codegraph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
