# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['silkaj']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.3,<2.0',
 'click>=7.0,<8.0',
 'duniterpy>=0.54.3,<0.55.0',
 'ipaddress>=1.0,<2.0',
 'tabulate>=0.8.3,<0.9.0',
 'texttable>=1.6,<2.0']

setup_kwargs = {
    'name': 'silkaj',
    'version': '0.7.4',
    'description': 'Powerfull, lightweight, and multi-platform command line client written with Python for Duniter’s currencies: Ğ1 and Ğ1-Test.',
    'long_description': '# Silkaj\n[![Version](https://img.shields.io/pypi/v/silkaj.svg)](https://pypi.python.org/pypi/silkaj) [![License](https://img.shields.io/pypi/l/silkaj.svg)](https://pypi.python.org/pypi/silkaj) [![Python versions](https://img.shields.io/pypi/pyversions/silkaj.svg)](https://pypi.python.org/pypi/silkaj)\n\n- CLI Duniter client written with Python 3.\n- [Website](https://silkaj.duniter.org)\n\n## Install\n```bash\npip3 install silkaj --user\n```\n\n- [Install with Pip](doc/install_pip.md)\n- [Install with pipenv](doc/install_pipenv.md)\n- [Install with the build](doc/install_build.md)\n- [Install with docker](doc/install_docker.md)\n- [Build an executable with Pyinstaller](doc/build_with_pyinstaller.md)\n\n## Usage\n- Get help usage with `-h` or `--help` options, then run:\n```bash\nsilkaj <sub-command>\n```\n\n- Will automatically request and post data on `duniter.org 443` main Ğ1 node.\n\n- Specify a custom node with `-p` option:\n```bash\nsilkaj -p <address>:<port> <sub-command>\n```\n\n## Features\n### Currency information\n- Currency information\n- Display the current Proof of Work difficulty level to generate the next block\n- Check the current network\n- Explore the blockchain block by block\n\n### Money management\n- Send transaction\n- Consult the wallet balance\n\n### Money management\n- Check sent and received certifications and consult the membership status of any given identity in the Web of Trust\n- Check the present currency information stand\n- Send certification\n\n### Authentication\n- Three authentication methods: Scrypt, file, and (E)WIF\n\n## Wrappers\n- [Install as a drop-down for GNOME\xa0Shell with Argos](doc/argos.md)\n- [How-to: automate transactions and multi-output](doc/how-to_automate_transactions_and_multi-output.md)\n- [Transaction generator written in Shell](https://gitlab.com/jytou/tgen)\n- [Ğ1Cotis](https://git.duniter.org/matograine/g1-cotis)\n- [Ğ1SMS](https://git.duniter.org/clients/G1SMS/)\n- [Ğmixer](https://git.duniter.org/tuxmain/gmixer-py/)\n\n### Dependencies\nSilkaj is based on Python dependencies:\n\n- [Click](https://click.palletsprojects.com/): Command Line Interface Creation Kit.\n- [DuniterPy](https://git.duniter.org/clients/python/duniterpy/): Python APIs library to implement duniter clients softwares.\n- [Tabulate](https://bitbucket.org/astanin/python-tabulate/overview): to display charts.\n- [PyNaCl](https://github.com/pyca/pynacl/): Cryptography (NaCl) library.\n\n### Names\nI wanted to call that program:\n- bamiyan\n- margouillat\n- lsociety\n- cashmere\n\nI finally called it `Silkaj` as `Silk` in esperanto.\n\n### Website\n- [Silkaj website sources](https://git.duniter.org/websites/silkaj_website/)\n',
    'author': 'Moul',
    'author_email': 'moul@moul.re',
    'maintainer': 'Moul',
    'maintainer_email': 'moul@moul.re',
    'url': 'https://silkaj.duniter.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5.3,<4.0.0',
}


setup(**setup_kwargs)
