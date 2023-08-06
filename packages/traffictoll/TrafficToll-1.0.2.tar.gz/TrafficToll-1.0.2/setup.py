# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['traffictoll']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.4.1,<0.5.0', 'psutil>=5.6.7,<6.0.0', 'ruamel.yamL>=0.16.6,<0.17.0']

entry_points = \
{'console_scripts': ['tt = traffictoll.__main__:main']}

setup_kwargs = {
    'name': 'traffictoll',
    'version': '1.0.2',
    'description': 'NetLimiter-like traffic shaping for Linux',
    'long_description': "# TrafficToll\nNetLimiter-like traffic shaping for Linux\n\n# Description\nTrafficToll allows you to limit download and upload bandwidth globally\n(per interface) and per process, even during the process' runtime.\n\nThe configuration can be easily adjusted and new limits applied at any\npoint, as opposed to similar tools which either can only apply fixed\nglobal limits to the interface, certain ports, or require you to start\nthe process through them (and thus restart the target process to change\nthe limits).\n\n# Usage\n`# tt device config`\n\nWhere `device` is the interface you want to limit (usually the one you\nconnect to the internet with). For example:\n\n* `# tt enp3s0 night.yaml --delay 0.5` (regular interface, check every\nhalf second for change in networked processes)\n* `# tt tun0 day.yaml --logging-level DEBUG` (VPN interface, adjust\nlogging level to DEBUG)\n\nCurrently TrafficToll works based on a YAML configuration file. The configuration file\nis best explained by example:\n\n```YAML\n# Global limits\ndownload: 500kbps\nupload: 100kbps\n\n# Matched process limits\nprocesses:\n  Vivaldi:\n    download: 100kbps\n    match:\n      - exe: /opt/vivaldi/vivaldi-bin\n\n  Discord:\n    download: 300kbps\n\n    # This won't work, the specified upload exceeds the global upload, it will\n    # be 100kb/s max\n    upload: 200kbps\n    match:\n      - exe: /opt/discord/Discord\n\n  JDownloader 2:\n    # JDownloader 2 obviously has its own traffic shaping, this is just here as\n    # an example to show that matching on something else than the executable's\n    # path is possible\n    download: 300kbps\n    match:\n      - cmdline: .* JDownloader.jar\n```\n\nUnits can be specified in all formats that `tc` supports, namely: bit \n(with and without suffix), kbit, mbit, gbit, tbit, bps, kbps, mbps,\ngbps, tbps. To specify in IEC units, replace the SI prefix (k-, m-, g-,\nt-) with IEC prefix (ki-, mi-, gi- and ti-) respectively.\n\nAll limits can be omitted, in which case obviously no limiting will be\napplied. A process is selected when all predicates in the match section\nmatch. Every attribute [`psutil.Process`](https://psutil.readthedocs.io/en/latest/index.html#psutil.Process)\nprovides on Linux can be matched on, using regular expressions.\n\nWhen you terminate `tt` using Ctrl+C all changes to the traffic\nscheduling will be reverted, allowing you to easily update the config\nand apply new limits.\n\n# Installation\n`$ pip install traffictoll`\n\n`tt` has to be run as root.\n\n# Screenshots\nBecause a picture is always nice, even for CLI applications:\n\n![](https://i.imgur.com/EsOla66.png)\n",
    'author': 'cryzed',
    'author_email': 'cryzed@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cryzed/TrafficToll',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
