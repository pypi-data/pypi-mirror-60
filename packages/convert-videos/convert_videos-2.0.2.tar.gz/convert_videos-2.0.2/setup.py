# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['convert_videos']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4.0,<0.5.0',
 'ffmpy>=0.2.2,<0.3.0',
 'video_utils>=2.0.4,<3.0.0']

entry_points = \
{'console_scripts': ['convert-videos = convert_videos.cli:main']}

setup_kwargs = {
    'name': 'convert-videos',
    'version': '2.0.2',
    'description': 'This tool allows bulk conversion of videos using ffmpeg',
    'long_description': '# Convert Videos\n\n![Test Status](https://github.com/justin8/convert_videos/workflows/Tests/badge.svg?branch=master)\n[![codecov](https://codecov.io/gh/justin8/convert_videos/branch/master/graph/badge.svg)](https://codecov.io/gh/justin8/convert_videos)\n\nThis tool allows bulk conversion of videos using ffmpeg\n\n## Usage\n\n```\nUsage: convert-videos [OPTIONS] DIRECTORY\n\nOptions:\n  -i, --in-place            Replace the original files instead of appending\n                            the new codec name\n  -f, --force               Force conversion even if the format of the file\n                            already matches the desired format\n  --video-codec TEXT        A target video codec  [default: HEVC]\n  -q, --quality INTEGER     The quantizer quality level to use  [default: 22]\n  -p, --preset TEXT         FFmpeg preset to use  [default: medium]\n  -w, --width INTEGER       Specify a new width to enable resizing of the\n                            video\n  -e, --extra-args TEXT     Specify any extra arguments you would like to pass\n                            to FFMpeg here\n  --audio-codec TEXT        A target audio codec  [default: AAC]\n  --audio-channels INTEGER  The number of channels to mux sound in to\n                            [default: 2]\n  --audio-bitrate INTEGER   The bitrate to use for the audio codec  [default:\n                            160]\n  --temp-dir TEXT           Specify a temporary directory to use during\n                            conversions instead of the system default\n  -v, --verbose             Enable verbose log output\n  --container TEXT          Specify a video container to convert the videos in\n                            to  [default: mkv]\n  -h, --help                Show this message and exit.\n\n```\n',
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
