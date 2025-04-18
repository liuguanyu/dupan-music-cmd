#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from dupan_music import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dupan-music",
    version=__version__,
    author="DuPan Music Team",
    author_email="example@example.com",
    description="百度盘音乐命令行播放器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dupan-music",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dupan-music/issues",
        "Documentation": "https://github.com/yourusername/dupan-music/docs",
        "Source Code": "https://github.com/yourusername/dupan-music",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Utilities",
    ],
    keywords="baidu, cloud, music, player, cli, command-line",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "qrcode>=7.0",
        "pillow>=8.0.0",
        "pydub>=0.25.0",
        "python-vlc>=3.0.0",
        "mutagen>=1.45.0",
        "tqdm>=4.60.0",
        "prompt_toolkit>=3.0.0",
        "pygments>=2.10.0",
    ],
    entry_points={
        "console_scripts": [
            "dupan-music=dupan_music.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
