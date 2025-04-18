#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交互式shell命令行接口
"""

import click

from dupan_music.shell.interactive import run_interactive_shell
from dupan_music.utils.logger import get_logger

logger = get_logger(__name__)


@click.command(help="启动交互式命令行界面")
def shell():
    """启动交互式命令行界面"""
    try:
        run_interactive_shell()
    except Exception as e:
        logger.exception(f"启动交互式shell失败: {str(e)}")
        click.echo(f"启动交互式shell失败: {str(e)}")
