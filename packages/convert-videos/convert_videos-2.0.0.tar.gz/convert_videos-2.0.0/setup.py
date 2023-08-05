# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['convert_videos']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4.3,<0.5.0',
 'ffmpy>=0.2.2,<0.3.0',
 'video_utils>=2.0.3,<3.0.0']

entry_points = \
{'console_scripts': ['convert-videos = convert_videos.cli:main']}

setup_kwargs = {
    'name': 'convert-videos',
    'version': '2.0.0',
    'description': 'This tool allows bulk conversion of videos using ffmpeg',
    'long_description': None,
    'author': 'Justin Dray',
    'author_email': 'justin@dray.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
