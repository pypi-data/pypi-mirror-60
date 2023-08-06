# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wormhole_ui', 'wormhole_ui.widgets.ui']

package_data = \
{'': ['*'],
 'wormhole_ui': ['widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/connect_dialog.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/errors.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/main_window.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/message_table.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/save_file_dialog.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/shutdown_message.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/ui_dialog.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py',
                 'widgets/util.py']}

install_requires = \
['PySide2==5.13.1',
 'humanize>=0.5.1,<0.6.0',
 'magic_wormhole>=0.11.2,<0.12.0',
 'qt5reactor>=0.6,<0.7']

entry_points = \
{'console_scripts': ['wormhole-ui = wormhole_ui.main:run']}

setup_kwargs = {
    'name': 'wormhole-ui',
    'version': '0.1.2',
    'description': 'UI for Magic Wormhole - get things from one computer to another safely',
    'long_description': None,
    'author': 'sneakypete81',
    'author_email': 'sneakypete81@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<3.9',
}


setup(**setup_kwargs)
