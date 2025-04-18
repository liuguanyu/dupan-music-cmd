#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API命令行接口
"""

import os
import sys
import json
import click
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import box

from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.utils.logger import get_logger
from dupan_music.utils.file_utils import format_size

logger = get_logger(__name__)
console = Console()

def get_api_instance() -> BaiduPanAPI:
    """获取API实例"""
    try:
        auth = BaiduPanAuth()
        if not auth.is_authenticated():
            console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
            sys.exit(1)
        return BaiduPanAPI(auth)
    except Exception as e:
        console.print(f"[red]初始化API失败: {str(e)}[/red]")
        sys.exit(1)

@click.group()
def api():
    """百度网盘API命令"""
    pass

@api.command()
@click.option('--path', '-p', default='/', help='文件路径')
@click.option('--order', '-o', default='name', type=click.Choice(['name', 'time', 'size']), help='排序方式')
@click.option('--desc/--asc', default=False, help='是否降序排序')
@click.option('--limit', '-l', default=100, help='返回条目数量限制')
@click.option('--folder-only', is_flag=True, help='只显示文件夹')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def list(path, order, desc, limit, folder_only, json_output):
    """列出文件"""
    api = get_api_instance()
    
    try:
        files = api.get_file_list(
            dir_path=path,
            order=order,
            desc=desc,
            limit=limit,
            folder=1 if folder_only else 0
        )
        
        if json_output:
            console.print(json.dumps(files, ensure_ascii=False, indent=2))
            return
        
        if not files:
            console.print(f"[yellow]路径 '{path}' 下没有文件[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("类型", style="dim", width=4)
        table.add_column("文件名", style="cyan")
        table.add_column("大小", justify="right")
        table.add_column("修改时间", style="green")
        table.add_column("文件ID", style="dim")
        
        for file in files:
            file_type = "📁" if file.get('isdir') == 1 else "📄"
            file_name = file.get('server_filename', 'Unknown')
            file_size = format_size(file.get('size', 0)) if file.get('isdir') == 0 else "-"
            file_time = str(file.get('server_mtime', 'Unknown'))
            file_id = str(file.get('fs_id', 'Unknown'))
            
            table.add_row(file_type, file_name, file_size, file_time, file_id)
        
        console.print(table)
        console.print(f"[bold green]共 {len(files)} 个项目[/bold green]")
    except Exception as e:
        console.print(f"[red]获取文件列表失败: {str(e)}[/red]")

@api.command()
@click.option('--path', '-p', default='/', help='文件路径')
@click.option('--order', '-o', default='name', type=click.Choice(['name', 'time', 'size']), help='排序方式')
@click.option('--desc/--asc', default=False, help='是否降序排序')
@click.option('--limit', '-l', default=100, help='返回条目数量限制')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def list_recursive(path, order, desc, limit, json_output):
    """递归列出文件"""
    api = get_api_instance()
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]获取文件列表...", total=None)
            files = api.get_file_list_recursive(
                dir_path=path,
                order=order,
                desc=desc,
                limit=limit
            )
            progress.update(task, completed=True)
        
        if json_output:
            console.print(json.dumps(files, ensure_ascii=False, indent=2))
            return
        
        if not files:
            console.print(f"[yellow]路径 '{path}' 下没有文件[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("类型", style="dim", width=4)
        table.add_column("文件名", style="cyan")
        table.add_column("路径", style="blue")
        table.add_column("大小", justify="right")
        table.add_column("文件ID", style="dim")
        
        for file in files:
            file_type = "📁" if file.get('isdir') == 1 else "📄"
            file_name = file.get('server_filename', 'Unknown')
            file_path = file.get('path', 'Unknown')
            file_size = format_size(file.get('size', 0)) if file.get('isdir') == 0 else "-"
            file_id = str(file.get('fs_id', 'Unknown'))
            
            table.add_row(file_type, file_name, file_path, file_size, file_id)
        
        console.print(table)
        console.print(f"[bold green]共 {len(files)} 个项目[/bold green]")
    except Exception as e:
        console.print(f"[red]获取文件列表失败: {str(e)}[/red]")

@api.command()
@click.argument('keyword')
@click.option('--path', '-p', default='/', help='搜索路径')
@click.option('--recursive/--no-recursive', default=True, help='是否递归搜索')
@click.option('--page', default=1, help='页码')
@click.option('--limit', '-l', default=100, help='每页数量')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def search(keyword, path, recursive, page, limit, json_output):
    """搜索文件"""
    api = get_api_instance()
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]搜索文件...", total=None)
            files = api.search_files(
                key=keyword,
                dir_path=path,
                recursion=1 if recursive else 0,
                page=page,
                num=limit
            )
            progress.update(task, completed=True)
        
        if json_output:
            console.print(json.dumps(files, ensure_ascii=False, indent=2))
            return
        
        if not files:
            console.print(f"[yellow]未找到匹配 '{keyword}' 的文件[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("类型", style="dim", width=4)
        table.add_column("文件名", style="cyan")
        table.add_column("路径", style="blue")
        table.add_column("大小", justify="right")
        table.add_column("文件ID", style="dim")
        
        for file in files:
            file_type = "📁" if file.get('isdir') == 1 else "📄"
            file_name = file.get('server_filename', 'Unknown')
            file_path = file.get('path', 'Unknown')
            file_size = format_size(file.get('size', 0)) if file.get('isdir') == 0 else "-"
            file_id = str(file.get('fs_id', 'Unknown'))
            
            table.add_row(file_type, file_name, file_path, file_size, file_id)
        
        console.print(table)
        console.print(f"[bold green]共找到 {len(files)} 个匹配项[/bold green]")
    except Exception as e:
        console.print(f"[red]搜索文件失败: {str(e)}[/red]")

@api.command()
@click.argument('file_id', type=int)
@click.option('--with-link', is_flag=True, help='获取下载链接')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def info(file_id, with_link, json_output):
    """获取文件信息"""
    api = get_api_instance()
    
    try:
        file_info = api.get_file_info([file_id], dlink=1 if with_link else 0)
        
        if not file_info:
            console.print(f"[yellow]未找到ID为 {file_id} 的文件[/yellow]")
            return
        
        if json_output:
            console.print(json.dumps(file_info, ensure_ascii=False, indent=2))
            return
        
        info = file_info[0]
        
        console.print(f"[bold cyan]文件信息:[/bold cyan]")
        console.print(f"[bold]文件名:[/bold] {info.get('filename', 'Unknown')}")
        console.print(f"[bold]路径:[/bold] {info.get('path', 'Unknown')}")
        console.print(f"[bold]大小:[/bold] {format_size(info.get('size', 0))}")
        console.print(f"[bold]文件ID:[/bold] {info.get('fs_id', 'Unknown')}")
        console.print(f"[bold]MD5:[/bold] {info.get('md5', 'Unknown')}")
        console.print(f"[bold]创建时间:[/bold] {info.get('server_ctime', 'Unknown')}")
        console.print(f"[bold]修改时间:[/bold] {info.get('server_mtime', 'Unknown')}")
        
        if with_link and 'dlink' in info:
            console.print(f"[bold]下载链接:[/bold] {info.get('dlink', 'Unknown')}")
    except Exception as e:
        console.print(f"[red]获取文件信息失败: {str(e)}[/red]")

@api.command()
@click.argument('file_id', type=int)
def download_link(file_id):
    """获取文件下载链接"""
    api = get_api_instance()
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]获取下载链接...", total=None)
            link = api.get_download_link(file_id)
            progress.update(task, completed=True)
        
        console.print(f"[bold green]下载链接:[/bold green] {link}")
    except Exception as e:
        console.print(f"[red]获取下载链接失败: {str(e)}[/red]")

@api.command()
@click.option('--path', '-p', default='/', help='文件路径')
@click.option('--order', '-o', default='name', type=click.Choice(['name', 'time', 'size']), help='排序方式')
@click.option('--desc/--asc', default=False, help='是否降序排序')
@click.option('--limit', '-l', default=100, help='返回条目数量限制')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def audio(path, order, desc, limit, json_output):
    """获取音频文件列表"""
    api = get_api_instance()
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]获取音频文件...", total=None)
            files = api.get_audio_files(
                dir_path=path,
                order=order,
                desc=desc,
                limit=limit
            )
            progress.update(task, completed=True)
        
        if json_output:
            console.print(json.dumps(files, ensure_ascii=False, indent=2))
            return
        
        if not files:
            console.print(f"[yellow]路径 '{path}' 下没有音频文件[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("序号", style="dim", width=4)
        table.add_column("文件名", style="cyan")
        table.add_column("路径", style="blue")
        table.add_column("大小", justify="right")
        table.add_column("文件ID", style="dim")
        
        for i, file in enumerate(files, 1):
            file_name = file.get('server_filename', 'Unknown')
            file_path = file.get('path', 'Unknown')
            file_size = format_size(file.get('size', 0))
            file_id = str(file.get('fs_id', 'Unknown'))
            
            table.add_row(str(i), file_name, file_path, file_size, file_id)
        
        console.print(table)
        console.print(f"[bold green]共 {len(files)} 个音频文件[/bold green]")
    except Exception as e:
        console.print(f"[red]获取音频文件列表失败: {str(e)}[/red]")

@api.command()
def user():
    """获取用户信息"""
    api = get_api_instance()
    
    try:
        user_info = api.get_user_info()
        
        console.print(f"[bold cyan]用户信息:[/bold cyan]")
        console.print(f"[bold]用户名:[/bold] {user_info.get('baidu_name', 'Unknown')}")
        console.print(f"[bold]网盘用户名:[/bold] {user_info.get('netdisk_name', 'Unknown')}")
        console.print(f"[bold]用户ID:[/bold] {user_info.get('uk', 'Unknown')}")
        console.print(f"[bold]头像URL:[/bold] {user_info.get('avatar_url', 'Unknown')}")
        console.print(f"[bold]VIP类型:[/bold] {user_info.get('vip_type', 0)}")
    except Exception as e:
        console.print(f"[red]获取用户信息失败: {str(e)}[/red]")

@api.command()
def quota():
    """获取网盘容量信息"""
    api = get_api_instance()
    
    try:
        quota_info = api.get_quota()
        
        total = quota_info.get('total', 0)
        used = quota_info.get('used', 0)
        free = total - used
        percent = (used / total) * 100 if total > 0 else 0
        
        console.print(f"[bold cyan]网盘容量信息:[/bold cyan]")
        console.print(f"[bold]总容量:[/bold] {format_size(total)}")
        console.print(f"[bold]已使用:[/bold] {format_size(used)} ({percent:.2f}%)")
        console.print(f"[bold]剩余容量:[/bold] {format_size(free)}")
    except Exception as e:
        console.print(f"[red]获取网盘容量信息失败: {str(e)}[/red]")
