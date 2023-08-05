# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bli']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bli = bli.bli:main']}

setup_kwargs = {
    'name': 'bli',
    'version': '0.1.2b0',
    'description': 'A todo-list manager with bullet-journal mechanisms',
    'long_description': '```text\n  _     _ _ \n | |   | (_)\n | |__ | |_ \n | \'_ \\| | |\n | |_) | | |\n |_.__/|_|_|\n```\n\n# bli\n\n**bli** is a simple cli tool to keep a journalised todo list.\n\nIt uses the bullet journal notation system and keeps an archive as `.txt` files, so everything will always be readable and accessible.\n\n\n## Installation\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install bli.\n\n```bash\npip install bli\n```\n\n## Usage\n```\n$ bli --help\n\nOptions:\n  --all / --no-all\n  -f, --filter TEXT\n  -a, --add TEXT\n  -x, --cross INTEGER\n  -r, --restore INTEGER\n  -v, --check INTEGER\n  -pp, ->, --postpone INTEGER\n  --help                       Show this message and exit.\n```\n\nUse the flags `-a|--add`, `-x|--delete`, `-v|--check` and `-pp|--postpone` to manage your tasks \n\n\n```bash\n$ bli --add "Do whatever" -a "Do something else" -a "Do It Now Said Shia LaBoeuf"\n0 • Do whatever\n1 • Do something else\n2 • Do It Now Said Shia LaBoeuf\n```\n```bash\n$ bli -v 0 -x 1\n2 • Do It Now Said Shia LaBoeuf\n```\n```\n$ bli --all\n0 v Do whatever\n1 x Do something else\n2 • Do It Now Said Shia LaBoeuf\n```\n\nEntries can be filtered using a string or a regex. Every filtering is **case-insensitive**.\n\n```\n$ bli -f \'/shia|whatever/\' --all\n0 v Do whatever\n2 • Do It Now Said Shia LaBoeuf\n```\n\nThen the next day, every undone task will automatically be postponed and available to the new page. \n\n```bash\n$ bli\n0 • Do It Now Said Shia LaBoeuf\n```\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'erawpalassalg',
    'author_email': 'mael.arnaud@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Erawpalassalg/clj',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
