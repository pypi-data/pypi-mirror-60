# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hypermodern_python']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'desert>=2020.1.6,<2021.0.0',
 'marshmallow>=3.3.0,<4.0.0',
 'requests>=2.22.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.5.0,<2.0.0']}

entry_points = \
{'console_scripts': ['hypermodern-python = hypermodern_python.console:main']}

setup_kwargs = {
    'name': 'hypermodern-python',
    'version': '0.2.1',
    'description': 'The hypermodern Python project',
    'long_description': '[![tests](https://github.com/cjolowicz/hypermodern-python/workflows/tests/badge.svg)](https://github.com/cjolowicz/hypermodern-python/actions?workflow=tests)\n[![Codecov](https://codecov.io/gh/cjolowicz/hypermodern-python/branch/master/graph/badge.svg)](https://codecov.io/gh/cjolowicz/hypermodern-python)\n[![PyPI](https://img.shields.io/pypi/v/hypermodern-python.svg)](https://pypi.org/project/hypermodern-python/)\n[![Read the Docs](https://readthedocs.org/projects/hypermodern-python/badge/)](https://hypermodern-python.readthedocs.io/)\n\n# hypermodern-python\n\nCompanion repository for the Hypermodern Python article series<br>\nhttps://medium.com/@cjolowicz/hypermodern-python-d44485d9d769\n',
    'author': 'Claudio Jolowicz',
    'author_email': 'mail@claudiojolowicz.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cjolowicz/hypermodern-python',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
