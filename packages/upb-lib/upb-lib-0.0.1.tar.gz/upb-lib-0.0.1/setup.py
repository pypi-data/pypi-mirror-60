# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['upb_lib']

package_data = \
{'': ['*']}

install_requires = \
['pyserial-asyncio>=0.4.0,<0.5.0', 'pytz>=2019']

setup_kwargs = {
    'name': 'upb-lib',
    'version': '0.0.1',
    'description': 'Library for interacting with UPB PIM.',
    'long_description': "# Python UPB Powerline Interface library\n\nLibrary for interacting with UPB PIM/CIM\n\nhttps://github.com/gwww/upb\n\n## Requirements\n\n- Python 3.7 (or higher)\n\n## Description\n\nThis package is created as a library to interact with an UPB PIM.\nThe motivation to write this was to use with the Home Assistant\nautomation platform. The library can be used for writing other UPB\napplications. The IO with the PIM is asynchronous over TCP or over the\nserial port.\n\n## Installation\n\n```bash\n    $ pip install upb_lib\n```\n\n## Overview\n\nDetails TBD\n  \nSimplest thing right now is when in the root of the git repo that you have cloned is to enter the command `bin/simple`. You need the environment variable `UPBPIM_URL` set. Mine is set to `serial:///dev/cu.KeySerial1` on a MacBook. What is constant is `serial://` followed by the USB port that the PIM is on, which in my case is `/dev/cu.KeySerial1`. On Windows is might be something like `COM1`.\n\nAlso required is a `UPStart` export file. Mine is in the `bin` directory and named `upb.upe`. The `simple` program looks for it there.\n\nThis is all under very active development and will change. But if you really want to get up and running... Go for it!\n\n## Development\n\nThis project uses [poetry](https://poetry.eustace.io/) for development dependencies. Installation instructions are on their website.\n\nTo get started developing:\n\n```\ngit clone https://github.com/gwww/upb.git\ncd upb\npoetry install\npoetry shell # Or activate the created virtual environment\nmake test # to ensure everything installed properly\n```\n\nThere is a `Makefile` in the root directory as well. The `make` command\nfollowed by one of the targets in the `Makefile` can be used. If you don't\nhave or wish to use `make` the `Makefile` serves as examples of common\ncommands that can be run.\n",
    'author': 'Glenn Waters',
    'author_email': 'gwwaters+upb@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gwww/upb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
