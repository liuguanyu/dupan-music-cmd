#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放列表命令行接口
"""

import os
import sys
import click
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem
from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.utils.logger import get_logger
from dupan_music.utils.file_utils import format_size

logger = get_logger(__name__)
console = Console()

def get_playlist_manager() -> PlaylistManager:
    """获取播放列表管理器实例"""
    try:
        # 获取API实例
        auth = BaiduPanAuth()
        if auth.is_authenticated():
            api = BaiduPanAPI(auth)
            return PlaylistManager(api)
        else:
            # 如果未登录，创建无API的播放列表管理器
            return PlaylistManager()
    except Exception as e:
        console.print(f"[red]初始化播放列表管理器失败: {str(e)}[/red]")
        sys.exit(1)

@click.group()
def playlist():
    """播放列表命令"""
    pass

@playlist.command("list")
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def list_playlists(json_output):
    """列出所有播放列表"""
    manager = get_playlist_manager()
    playlists = manager.get_all_playlists()
    
    if not playlists:
        console.print("[yellow]没有找到播放列表[/yellow]")
        return
    
    if json_output:
        import json
        data = [p.to_dict() for p in playlists]
        console.print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("名称", style="cyan")
    table.add_column("描述", style="green")
    table.add_column("歌曲数", justify="right")
    table.add_column("创建时间", style="dim")
    table.add_column("更新时间", style="dim")
    
    for playlist in playlists:
        name = playlist.name
        description = playlist.description
        count = len(playlist.items)
        create_time = datetime.fromtimestamp(playlist.create_time).strftime('%Y-%m-%d %H:%M:%S')
        update_time = datetime.fromtimestamp(playlist.update_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # 如果是最近播放列表，添加特殊标记
        if name == PlaylistManager.RECENT_PLAYLIST_NAME:
            name = f"[bold]{name}[/bold]"
        
        table.add_row(name, description, str(count), create_time, update_time)
    
    console.print(table)
    console.print(f"[bold green]共 {len(playlists)} 个播放列表[/bold green]")

@playlist.command("show")
@click.argument('name')
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def show_playlist(name, json_output):
    """显示播放列表内容"""
    manager = get_playlist_manager()
    playlist = manager.get_playlist(name)
    
    if not playlist:
        console.print(f"[red]播放列表 '{name}' 不存在[/red]")
        return
    
    if json_output:
        import json
        console.print(json.dumps(playlist.to_dict(), ensure_ascii=False, indent=2))
        return
    
    items = playlist.items
    
    if not items:
        console.print(f"[yellow]播放列表 '{name}' 为空[/yellow]")
        return
    
    # 显示播放列表信息
    console.print(Panel(f"[bold]{playlist.name}[/bold]\n{playlist.description}", 
                        title="播放列表信息", border_style="cyan"))
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("序号", style="dim", width=4)
    table.add_column("文件名", style="cyan")
    table.add_column("路径", style="blue")
    table.add_column("大小", justify="right")
    table.add_column("文件ID", style="dim")
    
    for i, item in enumerate(items, 1):
        file_name = item.server_filename
        file_path = item.path
        file_size = format_size(item.size)
        file_id = str(item.fs_id)
        
        table.add_row(str(i), file_name, file_path, file_size, file_id)
    
    console.print(table)
    console.print(f"[bold green]共 {len(items)} 首歌曲[/bold green]")

@playlist.command("create")
@click.argument('name')
@click.option('--description', '-d', default='', help='播放列表描述')
def create_playlist(name, description):
    """创建新播放列表"""
    manager = get_playlist_manager()
    
    # 检查是否已存在
    if manager.get_playlist(name):
        console.print(f"[red]播放列表 '{name}' 已存在[/red]")
        return
    
    # 创建播放列表
    playlist = manager.create_playlist(name, description)
    
    if playlist:
        console.print(f"[green]已成功创建播放列表 '{name}'[/green]")
    else:
        console.print(f"[red]创建播放列表 '{name}' 失败[/red]")

@playlist.command("delete")
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='强制删除，不确认')
def delete_playlist(name, force):
    """删除播放列表"""
    manager = get_playlist_manager()
    
    # 检查是否存在
    if not manager.get_playlist(name):
        console.print(f"[red]播放列表 '{name}' 不存在[/red]")
        return
    
    # 确认删除
    if not force and not Confirm.ask(f"确定要删除播放列表 '{name}' 吗?"):
        console.print("[yellow]已取消删除[/yellow]")
        return
    
    # 删除播放列表
    success = manager.delete_playlist(name)
    
    if success:
        console.print(f"[green]已成功删除播放列表 '{name}'[/green]")
    else:
        console.print(f"[red]删除播放列表 '{name}' 失败[/red]")

@playlist.command("add")
@click.argument('playlist_name')
@click.argument('file_ids', nargs=-1, type=int)
def add_to_playlist(playlist_name, file_ids):
    """添加文件到播放列表"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 检查是否有API
    if not manager.api:
        console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
        return
    
    # 添加文件
    success_count = 0
    for fs_id in file_ids:
        try:
            # 获取文件信息
            file_info = manager.api.get_file_info([fs_id])
            
            if not file_info:
                console.print(f"[red]文件ID {fs_id} 不存在[/red]")
                continue
            
            # 添加到播放列表
            success = manager.add_to_playlist(playlist_name, file_info[0])
            
            if success:
                success_count += 1
                console.print(f"[green]已添加文件 '{file_info[0].get('server_filename')}' 到播放列表[/green]")
            else:
                console.print(f"[red]添加文件 '{file_info[0].get('server_filename')}' 失败[/red]")
        except Exception as e:
            console.print(f"[red]添加文件ID {fs_id} 失败: {str(e)}[/red]")
    
    console.print(f"[bold green]共成功添加 {success_count}/{len(file_ids)} 个文件[/bold green]")

@playlist.command("remove")
@click.argument('playlist_name')
@click.argument('file_ids', nargs=-1, type=int)
def remove_from_playlist(playlist_name, file_ids):
    """从播放列表移除文件"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 移除文件
    success_count = 0
    for fs_id in file_ids:
        success = manager.remove_from_playlist(playlist_name, fs_id)
        
        if success:
            success_count += 1
            console.print(f"[green]已从播放列表移除文件ID {fs_id}[/green]")
        else:
            console.print(f"[red]从播放列表移除文件ID {fs_id} 失败[/red]")
    
    console.print(f"[bold green]共成功移除 {success_count}/{len(file_ids)} 个文件[/bold green]")

@playlist.command("clear")
@click.argument('playlist_name')
@click.option('--force', '-f', is_flag=True, help='强制清空，不确认')
def clear_playlist(playlist_name, force):
    """清空播放列表"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 确认清空
    if not force and not Confirm.ask(f"确定要清空播放列表 '{playlist_name}' 吗?"):
        console.print("[yellow]已取消清空[/yellow]")
        return
    
    # 清空播放列表
    playlist.clear()
    manager.save_playlist(playlist)
    
    console.print(f"[green]已成功清空播放列表 '{playlist_name}'[/green]")

@playlist.command("sort")
@click.argument('playlist_name')
@click.option('--key', '-k', type=click.Choice(['name', 'time', 'size', 'add_time']), 
              default='name', help='排序键')
@click.option('--desc/--asc', default=False, help='是否降序排序')
def sort_playlist(playlist_name, key, desc):
    """排序播放列表"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 排序播放列表
    playlist.sort_by(key, desc)
    manager.save_playlist(playlist)
    
    order_type = "降序" if desc else "升序"
    console.print(f"[green]已成功按 {key} {order_type}排序播放列表 '{playlist_name}'[/green]")

@playlist.command("recent")
@click.option('--json', 'json_output', is_flag=True, help='以JSON格式输出')
def show_recent(json_output):
    """显示最近播放列表"""
    manager = get_playlist_manager()
    recent = manager.get_playlist(PlaylistManager.RECENT_PLAYLIST_NAME)
    
    if not recent:
        console.print("[red]最近播放列表不存在[/red]")
        return
    
    if json_output:
        import json
        console.print(json.dumps(recent.to_dict(), ensure_ascii=False, indent=2))
        return
    
    items = recent.items
    
    if not items:
        console.print("[yellow]最近播放列表为空[/yellow]")
        return
    
    # 显示最近播放列表
    console.print(Panel("[bold]最近播放列表[/bold]\n自动记录最近播放的音乐", 
                        title="播放列表信息", border_style="cyan"))
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("序号", style="dim", width=4)
    table.add_column("文件名", style="cyan")
    table.add_column("路径", style="blue")
    table.add_column("大小", justify="right")
    table.add_column("文件ID", style="dim")
    
    for i, item in enumerate(items, 1):
        file_name = item.server_filename
        file_path = item.path
        file_size = format_size(item.size)
        file_id = str(item.fs_id)
        
        table.add_row(str(i), file_name, file_path, file_size, file_id)
    
    console.print(table)
    console.print(f"[bold green]共 {len(items)} 首歌曲[/bold green]")

@playlist.command("add-from-path")
@click.argument('playlist_name')
@click.argument('path', default='/')
@click.option('--recursive/--no-recursive', default=False, help='是否递归添加')
def add_from_path(playlist_name, path, recursive):
    """从路径添加文件到播放列表"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 检查是否有API
    if not manager.api:
        console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
        return
    
    # 获取音频文件
    try:
        console.print(f"[cyan]正在获取路径 '{path}' 下的音频文件...[/cyan]")
        
        if recursive:
            files = manager.api.get_audio_files_recursive(path)
        else:
            files = manager.api.get_audio_files(path)
        
        if not files:
            console.print(f"[yellow]路径 '{path}' 下没有音频文件[/yellow]")
            return
        
        # 添加文件
        success_count = 0
        for file in files:
            success = manager.add_to_playlist(playlist_name, file)
            
            if success:
                success_count += 1
                console.print(f"[green]已添加文件 '{file.get('server_filename')}' 到播放列表[/green]")
        
        console.print(f"[bold green]共成功添加 {success_count}/{len(files)} 个文件[/bold green]")
    except Exception as e:
        console.print(f"[red]添加文件失败: {str(e)}[/red]")

@playlist.command("verify")
@click.argument('playlist_name')
@click.option('--auto-refresh', is_flag=True, help='自动刷新无效文件')
def verify_playlist(playlist_name, auto_refresh):
    """验证播放列表文件有效性"""
    manager = get_playlist_manager()
    
    # 检查播放列表是否存在
    playlist = manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 检查是否有API
    if not manager.api:
        console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
        return
    
    # 验证文件
    invalid_items = []
    refreshed_items = []
    
    console.print(f"[cyan]正在验证播放列表 '{playlist_name}' 中的文件...[/cyan]")
    
    for i, item in enumerate(playlist.items):
        valid = manager.check_file_validity(item.fs_id)
        
        if not valid:
            console.print(f"[yellow]文件 '{item.server_filename}' 无效[/yellow]")
            invalid_items.append(i)
            
            # 尝试刷新
            if auto_refresh:
                refreshed_info = manager.refresh_file(item.fs_id)
                
                if refreshed_info:
                    # 更新文件信息
                    new_item = PlaylistItem.from_api_result(refreshed_info)
                    playlist.items[i] = new_item
                    refreshed_items.append(item.server_filename)
                    console.print(f"[green]已刷新文件 '{item.server_filename}'[/green]")
    
    # 保存更新后的播放列表
    if refreshed_items:
        manager.save_playlist(playlist)
        console.print(f"[bold green]已成功刷新 {len(refreshed_items)} 个文件[/bold green]")
    
    # 显示结果
    if not invalid_items:
        console.print(f"[bold green]播放列表 '{playlist_name}' 中的所有文件都有效[/bold green]")
    elif not auto_refresh:
        console.print(f"[bold yellow]播放列表 '{playlist_name}' 中有 {len(invalid_items)} 个无效文件[/bold yellow]")
        console.print("[yellow]提示: 使用 --auto-refresh 选项可自动刷新无效文件[/yellow]")

if __name__ == "__main__":
    playlist()
