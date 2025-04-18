#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主模块，命令行入口
"""

import click
from rich.console import Console
from rich.panel import Panel

from dupan_music import __version__
from dupan_music.auth.cli import auth
from dupan_music.api.cli import api
from dupan_music.utils.logger import LOGGER


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="dupan-music")
def main():
    """百度盘音乐命令行播放器"""
    pass


# 添加子命令
main.add_command(auth)
main.add_command(api)


@main.command("version")
def version():
    """显示版本信息"""
    console.print(Panel(f"百度盘音乐命令行播放器 v{__version__}"))


if __name__ == "__main__":
    main()
