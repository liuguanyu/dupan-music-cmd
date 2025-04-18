#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API命令行接口
"""

import os
import sys
import json
import click
from typing import Dict, List, Optional, Set, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box

from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.playlist.playlist import PlaylistManager
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

@api.command("select-files")
@click.option('--playlist', '-p', help='要添加文件的播放列表名称')
@click.option('--start-path', default='/', help='起始路径')
def select_files(playlist, start_path):
    """交互式选择文件（过滤不支持的文件类型）"""
    api = get_api_instance()
    
    # 如果指定了播放列表，检查是否存在
    playlist_manager = None
    if playlist:
        try:
            auth = BaiduPanAuth()
            if auth.is_authenticated():
                playlist_manager = PlaylistManager(api)
                if not playlist_manager.get_playlist(playlist):
                    console.print(f"[red]播放列表 '{playlist}' 不存在[/red]")
                    return
            else:
                console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
                return
        except Exception as e:
            console.print(f"[red]初始化播放列表管理器失败: {str(e)}[/red]")
            return
    
    # 支持的音频文件扩展名
    audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']
    
    # 已选择的文件
    selected_files = []
    
    # 当前路径
    current_path = start_path
    
    # 历史路径栈
    path_history = []
    
    # 文件浏览循环
    while True:
        try:
            # 获取当前目录下的文件和文件夹
            files = api.get_file_list(dir_path=current_path)
            
            # 分离文件夹和音频文件
            folders = []
            audio_files = []
            
            for file in files:
                if file.get('isdir') == 1:
                    folders.append(file)
                elif os.path.splitext(file.get('server_filename', ''))[1].lower() in audio_extensions:
                    audio_files.append(file)
            
            # 按名称排序
            folders.sort(key=lambda x: x.get('server_filename', '').lower())
            audio_files.sort(key=lambda x: x.get('server_filename', '').lower())
            
            # 显示当前路径
            console.print(Panel(f"[bold cyan]当前路径: {current_path}[/bold cyan]", 
                               border_style="blue"))
            
            # 显示已选择的文件数量
            if selected_files:
                console.print(f"[bold green]已选择 {len(selected_files)} 个文件[/bold green]")
            
            # 创建表格显示文件和文件夹
            table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            table.add_column("序号", style="dim", width=4)
            table.add_column("类型", style="dim", width=4)
            table.add_column("名称", style="cyan")
            table.add_column("大小", justify="right")
            table.add_column("文件ID", style="dim")
            
            # 添加返回上级目录选项
            if current_path != '/':
                table.add_row("0", "📂", "[yellow]..（返回上级目录）[/yellow]", "-", "-")
            
            # 添加文件夹
            for i, folder in enumerate(folders, 1):
                folder_name = folder.get('server_filename', 'Unknown')
                folder_id = str(folder.get('fs_id', 'Unknown'))
                
                table.add_row(str(i), "📁", folder_name, "-", folder_id)
            
            # 添加音频文件
            for i, file in enumerate(audio_files, len(folders) + 1):
                file_name = file.get('server_filename', 'Unknown')
                file_size = format_size(file.get('size', 0))
                file_id = str(file.get('fs_id', 'Unknown'))
                
                # 检查文件是否已被选择
                is_selected = any(f.get('fs_id') == file.get('fs_id') for f in selected_files)
                
                if is_selected:
                    table.add_row(str(i), "🎵", f"[bold green]{file_name}[/bold green]", 
                                 f"[bold green]{file_size}[/bold green]", 
                                 f"[bold green]{file_id}[/bold green]")
                else:
                    table.add_row(str(i), "🎵", file_name, file_size, file_id)
            
            # 显示表格
            console.print(table)
            
            # 显示操作提示
            console.print("\n[bold]操作说明:[/bold]")
            console.print("  输入序号: 选择文件夹或文件")
            console.print("  输入多个序号(用空格分隔): 选择多个文件")
            console.print("  a: 选择当前目录下所有音频文件")
            console.print("  c: 清除所有已选择的文件")
            console.print("  d: 完成选择并添加到播放列表")
            console.print("  q: 退出")
            
            # 获取用户输入
            choice = Prompt.ask("\n请输入您的选择")
            
            # 处理用户输入
            if choice.lower() == 'q':
                # 退出
                if selected_files and Confirm.ask("您有未保存的选择，确定要退出吗?"):
                    break
                elif not selected_files:
                    break
            elif choice.lower() == 'a':
                # 选择所有音频文件
                for file in audio_files:
                    if not any(f.get('fs_id') == file.get('fs_id') for f in selected_files):
                        selected_files.append(file)
                console.print("[green]已选择当前目录下所有音频文件[/green]")
            elif choice.lower() == 'c':
                # 清除所有选择
                if selected_files:
                    if Confirm.ask("确定要清除所有已选择的文件吗?"):
                        selected_files = []
                        console.print("[yellow]已清除所有选择[/yellow]")
                else:
                    console.print("[yellow]当前没有选择任何文件[/yellow]")
            elif choice.lower() == 'd':
                # 完成选择
                if not selected_files:
                    console.print("[yellow]您尚未选择任何文件[/yellow]")
                    continue
                
                # 如果没有指定播放列表，询问用户
                if not playlist:
                    # 获取所有播放列表
                    playlists = playlist_manager.get_all_playlists() if playlist_manager else []
                    
                    if not playlists:
                        console.print("[yellow]没有找到播放列表，请先创建一个播放列表[/yellow]")
                        if Confirm.ask("是否退出文件选择?"):
                            break
                        continue
                    
                    # 显示播放列表
                    console.print("[bold cyan]可用的播放列表:[/bold cyan]")
                    for i, p in enumerate(playlists, 1):
                        console.print(f"{i}. {p.name} - {p.description}")
                    
                    # 让用户选择播放列表
                    playlist_choice = Prompt.ask("请选择要添加到的播放列表", choices=[str(i) for i in range(1, len(playlists) + 1)])
                    selected_playlist = playlists[int(playlist_choice) - 1].name
                else:
                    selected_playlist = playlist
                
                # 添加文件到播放列表
                success_count = 0
                for file in selected_files:
                    success = playlist_manager.add_to_playlist(selected_playlist, file)
                    if success:
                        success_count += 1
                
                console.print(f"[bold green]已成功添加 {success_count}/{len(selected_files)} 个文件到播放列表 '{selected_playlist}'[/bold green]")
                break
            else:
                # 处理序号选择
                try:
                    # 检查是否是多选
                    if ' ' in choice:
                        # 多选文件
                        indices = [int(idx) for idx in choice.split()]
                        for idx in indices:
                            # 确保索引有效且不是文件夹
                            if 1 <= idx <= len(folders) + len(audio_files):
                                if idx > len(folders):  # 是音频文件
                                    file = audio_files[idx - len(folders) - 1]
                                    # 检查是否已选择
                                    if not any(f.get('fs_id') == file.get('fs_id') for f in selected_files):
                                        selected_files.append(file)
                                        console.print(f"[green]已选择: {file.get('server_filename')}[/green]")
                                    else:
                                        # 取消选择
                                        selected_files = [f for f in selected_files if f.get('fs_id') != file.get('fs_id')]
                                        console.print(f"[yellow]已取消选择: {file.get('server_filename')}[/yellow]")
                                else:
                                    console.print("[yellow]不能选择文件夹，请进入文件夹选择文件[/yellow]")
                            else:
                                console.print(f"[red]无效的序号: {idx}[/red]")
                    else:
                        # 单选
                        idx = int(choice)
                        
                        # 处理返回上级目录
                        if idx == 0 and current_path != '/':
                            # 返回上级目录
                            current_path = os.path.dirname(current_path.rstrip('/'))
                            if current_path == '':
                                current_path = '/'
                            continue
                        
                        # 处理文件夹选择
                        if 1 <= idx <= len(folders):
                            folder = folders[idx - 1]
                            path_history.append(current_path)
                            current_path = folder.get('path')
                        # 处理文件选择
                        elif len(folders) < idx <= len(folders) + len(audio_files):
                            file = audio_files[idx - len(folders) - 1]
                            # 检查文件是否已选择
                            if not any(f.get('fs_id') == file.get('fs_id') for f in selected_files):
                                selected_files.append(file)
                                console.print(f"[green]已选择: {file.get('server_filename')}[/green]")
                            else:
                                # 取消选择
                                selected_files = [f for f in selected_files if f.get('fs_id') != file.get('fs_id')]
                                console.print(f"[yellow]已取消选择: {file.get('server_filename')}[/yellow]")
                        else:
                            console.print(f"[red]无效的序号: {idx}[/red]")
                except ValueError:
                    console.print("[red]请输入有效的序号或命令[/red]")
                except Exception as e:
                    console.print(f"[red]处理选择时出错: {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red]处理文件浏览时出错: {str(e)}[/red]")
            break

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
