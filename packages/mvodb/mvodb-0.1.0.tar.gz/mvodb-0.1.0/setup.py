# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mvodb']

package_data = \
{'': ['*']}

install_requires = \
['guessit>=3.1.0,<4.0.0',
 'langdetect>=1.0.7,<2.0.0',
 'tmdbsimple>=2.2.0,<3.0.0']

entry_points = \
{'console_scripts': ['mvodb = mvodb.cli:main']}

setup_kwargs = {
    'name': 'mvodb',
    'version': '0.1.0',
    'description': 'Rename and move files using metadata from online databases.',
    'long_description': '<!--\nIMPORTANT:\n  This file is generated from the template at \'scripts/templates/README.md\'.\n  Please update the template instead of this file.\n-->\n\n# mvodb\n[![pipeline status](https://gitlab.com/pawamoy/mvodb/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/mvodb/pipelines)\n[![coverage report](https://gitlab.com/pawamoy/mvodb/badges/master/coverage.svg)](https://gitlab.com/pawamoy/mvodb/commits/master)\n[![documentation](https://img.shields.io/readthedocs/mvodb.svg?style=flat)](https://mvodb.readthedocs.io/en/latest/index.html)\n[![pypi version](https://img.shields.io/pypi/v/mvodb.svg)](https://pypi.org/project/mvodb/)\n\nRename and move files using metadata from online databases.\n\n## Requirements\nmvodb requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.8\n\n# make it available globally\npyenv global system 3.6.8\n```\n</details>\n\n## Installation\nWith `pip`:\n```bash\npython3.6 -m pip install mvodb\n```\n\nWith [`pipx`](https://github.com/cs01/pipx):\n```bash\npython3.6 -m pip install --user pipx\n\npipx install --python python3.6 mvodb\n```\n\n## Usage (as a library)\nTODO\n\n## Usage (command-line)\n```\nusage: mvodb [-h] [-y] FILE [FILE ...]\n\npositional arguments:\n  FILE              Files to move/rename.\n\noptional arguments:\n  -h, --help        show this help message and exit\n  -y, --no-confirm  Do not ask confirmation.\n\n```\n\n\n',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pawamoy/mvodb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
