# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['changelog_gen', 'changelog_gen.cli']

package_data = \
{'': ['*']}

install_requires = \
['bump2version>=0.5.11,<0.6.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['changelog-gen = changelog_gen.cli.command:gen',
                     'changelog-init = changelog_gen.cli.command:init']}

setup_kwargs = {
    'name': 'changelog-gen',
    'version': '0.2.3',
    'description': 'Changelog generation tool',
    'long_description': "# Changelog Generator - v0.2.3\n\n`changelog-gen` is a CHANGELOG generator intended to be used in conjunction\nwith [bumpversion](https://github.com/c4urself/bump2version) to generate\nchangelogs and create release tags.\n\n## Installation\n\n```bash\npip install changelog-gen\n```\n\nor clone this repo and install with poetry, currently depends on poetry < 1.0.0\ndue to other personal projects being stuck.\n\n```bash\npoetry install\n```\n\n## Usage\n\n`changelog-gen` currently only supports reading changes from a `release_notes` folder.\n\nFiles in the folder should use the format `{issue_number}.{type}`, supported\ntypes are currently `fix` and `feat`. The contents of the file is used to populate\nthe changelog file.\n\n```bash\n$ changelog-gen\n\n## v0.2.3\n\n### Bug fixes\n\n- Raise errors from internal classes, don't use click.echo() [#4]\n- Update changelog line format to include issue number at the end. [#7]\n\nWrite CHANGELOG for suggested version 0.2.3 [y/N]: y\n```\n",
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'url': 'https://github.com/EdgyEdgemond/changelog-gen/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
