# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xrandroll']

package_data = \
{'': ['*']}

install_requires = \
['pyside2>5.14']

entry_points = \
{'console_scripts': ['xrandroll = xrandroll:main']}

setup_kwargs = {
    'name': 'xrandroll',
    'version': '0.1.0',
    'description': 'A powertool to configure your display',
    'long_description': '# RandRoll\n\nNone of the existing display configuration tools does what I think is "the right thing".\nSo I went and wrote one.\n\n## The Right Thing\n\n* Don\'t start from a stored config, use xrandr to read the systems\' current state\n* Allow creating "profiles" that will get applied smartly (not there yet)\n* Generate a xrandr invocation to reflect the desired configuration\n* Allow per-monitor scaling\n* Allow arbitrary monitor positioning\n* Implement "scale everything so all the pixels are the same size" (not done yet)\n\n## To try:\n\nIf you have PySide2: `python -m xrandroll` in the folder where main.py is located.\n\n## TODO:\n\n* Implement other things\n* Make it a proper app, with installation and whatnot\n* Forget about it forever\n',
    'author': 'Roberto Alsina',
    'author_email': 'roberto.alsina@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.6',
}


setup(**setup_kwargs)
