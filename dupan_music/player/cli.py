#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器命令行接口
"""

import os
import sys
import time
import click
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from rich import box

from dupan_music.player.player import AudioPlayer
from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem
from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.utils.logger import get_logger
from dupan_music.utils.file_utils import format_size, format_time

logger = get_logger(__name__)
console = Console()

def get_player() -> AudioPlayer:
    """获取播放器实例"""
    try:
        # 获取API实例
        auth = BaiduPanAuth()
        if auth.is_authenticated():
            api = BaiduPanAPI(auth)
            playlist_manager = PlaylistManager(api)
            return AudioPlayer(api, playlist_manager)
        else:
            console.print("[red]您尚未登录，请先运行 'dupan-music login' 命令登录[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]初始化播放器失败: {str(e)}[/red]")
        sys.exit(1)

@click.group()
def player():
    """播放器命令"""
    pass

@player.command("play")
@click.argument('playlist_name')
@click.option('--index', '-i', type=int, default=0, help='播放索引')
def play_playlist(playlist_name, index):
    """播放指定播放列表"""
    # 获取播放器实例
    audio_player = get_player()
    
    # 获取播放列表管理器
    playlist_manager = audio_player.playlist_manager
    if not playlist_manager:
        console.print("[red]获取播放列表管理器失败[/red]")
        return
    
    # 获取播放列表
    playlist = playlist_manager.get_playlist(playlist_name)
    if not playlist:
        console.print(f"[red]播放列表 '{playlist_name}' 不存在[/red]")
        return
    
    # 检查播放列表是否为空
    if not playlist.items:
        console.print(f"[yellow]播放列表 '{playlist_name}' 为空[/yellow]")
        return
    
    # 检查索引是否有效
    if index < 0 or index >= len(playlist.items):
        console.print(f"[red]无效的播放索引: {index}[/red]")
        return
    
    # 设置播放列表
    audio_player.set_playlist(playlist)
    
    # 显示播放列表信息
    console.print(Panel(f"[bold]{playlist.name}[/bold]\n{playlist.description}", 
                        title="正在播放", border_style="cyan"))
    
    # 显示播放列表内容
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("序号", style="dim", width=4)
    table.add_column("文件名", style="cyan")
    table.add_column("路径", style="blue")
    table.add_column("大小", justify="right")
    
    for i, item in enumerate(playlist.items):
        file_name = item.server_filename
        file_path = item.path
        file_size = format_size(item.size)
        
        # 高亮当前播放项
        if i == index:
            table.add_row(f"[bold green]>{i+1}[/bold green]", 
                          f"[bold green]{file_name}[/bold green]", 
                          f"[bold green]{file_path}[/bold green]", 
                          f"[bold green]{file_size}[/bold green]")
        else:
            table.add_row(str(i+1), file_name, file_path, file_size)
    
    console.print(table)
    
    # 开始播放
    console.print(f"[cyan]正在播放: {playlist.items[index].server_filename}[/cyan]")
    success = audio_player.play(index)
    
    if not success:
        console.print("[red]播放失败[/red]")
        return
    
    # 设置回调函数
    def on_play(item):
        console.print(f"[green]正在播放: {item.server_filename}[/green]")
    
    def on_pause():
        console.print("[yellow]已暂停[/yellow]")
    
    def on_stop():
        console.print("[yellow]已停止[/yellow]")
    
    def on_next(item):
        console.print(f"[green]下一曲: {item.server_filename}[/green]")
    
    def on_prev(item):
        console.print(f"[green]上一曲: {item.server_filename}[/green]")
    
    def on_complete():
        console.print("[green]播放完成[/green]")
    
    audio_player.on_play_callback = on_play
    audio_player.on_pause_callback = on_pause
    audio_player.on_stop_callback = on_stop
    audio_player.on_next_callback = on_next
    audio_player.on_prev_callback = on_prev
    audio_player.on_complete_callback = on_complete
    
    # 交互式控制
    console.print("\n[bold]播放控制:[/bold]")
    console.print("  [cyan]空格[/cyan]: 暂停/恢复")
    console.print("  [cyan]n[/cyan]: 下一曲")
    console.print("  [cyan]p[/cyan]: 上一曲")
    console.print("  [cyan]+[/cyan]: 增加音量")
    console.print("  [cyan]-[/cyan]: 减小音量")
    console.print("  [cyan]q[/cyan]: 退出")
    
    # 显示进度条
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.fields[time]}"),
        TextColumn("音量: [yellow]{task.fields[volume]}%"),
        refresh_per_second=5,
    ) as progress:
        task = progress.add_task("播放中...", total=None, time="00:00 / 00:00", volume=audio_player.get_volume())
        
        try:
            while audio_player.is_playing:
                # 更新进度
                current_time = audio_player.get_time()
                total_time = audio_player.get_length()
                
                if total_time > 0:
                    progress.update(
                        task, 
                        completed=current_time,
                        total=total_time,
                        time=f"{format_time(current_time)} / {format_time(total_time)}",
                        volume=audio_player.get_volume()
                    )
                
                # 检查按键
                if os.name == 'nt':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore')
                        handle_key_press(key, audio_player)
                else:
                    # 非阻塞方式获取按键
                    try:
                        import select
                        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                            key = sys.stdin.read(1)
                            handle_key_press(key, audio_player)
                    except Exception as e:
                        logger.error(f"获取按键失败: {str(e)}")
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            audio_player.stop()
            console.print("[yellow]已退出播放[/yellow]")

def handle_key_press(key, player):
    """处理按键"""
    if key == ' ':
        # 暂停/恢复
        player.pause()
    elif key == 'n':
        # 下一曲
        player.next()
    elif key == 'p':
        # 上一曲
        player.prev()
    elif key == '+':
        # 增加音量
        current_volume = player.get_volume()
        player.set_volume(current_volume + 5)
    elif key == '-':
        # 减小音量
        current_volume = player.get_volume()
        player.set_volume(current_volume - 5)
    elif key == 'q':
        # 退出
        player.stop()

@player.command("play-file")
@click.argument('fs_id')
def play_single_file(fs_id):
    """播放指定文件"""
    from dupan_music.player.play_file import play_file
    play_file(fs_id)

@player.command("pause")
def pause_playback():
    """暂停/恢复播放"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    result = audio_player.pause()
    
    if result:
        status = "恢复" if not audio_player.is_paused else "暂停"
        console.print(f"[green]已{status}播放[/green]")
    else:
        console.print("[red]操作失败[/red]")

@player.command("stop")
def stop_playback():
    """停止播放"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    result = audio_player.stop()
    
    if result:
        console.print("[green]已停止播放[/green]")
    else:
        console.print("[red]停止播放失败[/red]")

@player.command("next")
def next_track():
    """播放下一曲"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    result = audio_player.next()
    
    if result:
        console.print(f"[green]正在播放下一曲: {audio_player.current_item.server_filename}[/green]")
    else:
        console.print("[red]播放下一曲失败[/red]")

@player.command("prev")
def prev_track():
    """播放上一曲"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    result = audio_player.prev()
    
    if result:
        console.print(f"[green]正在播放上一曲: {audio_player.current_item.server_filename}[/green]")
    else:
        console.print("[red]播放上一曲失败[/red]")

@player.command("volume")
@click.argument('level', type=int)
def set_volume(level):
    """设置音量 (0-100)"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    # 限制音量范围
    level = max(0, min(100, level))
    
    result = audio_player.set_volume(level)
    
    if result:
        console.print(f"[green]已设置音量: {level}%[/green]")
    else:
        console.print("[red]设置音量失败[/red]")

@player.command("status")
def show_status():
    """显示当前播放状态"""
    audio_player = get_player()
    
    if not audio_player.is_playing:
        console.print("[yellow]当前没有播放[/yellow]")
        return
    
    # 获取当前播放信息
    current_item = audio_player.current_item
    if not current_item:
        console.print("[yellow]没有正在播放的曲目[/yellow]")
        return
    
    # 获取播放状态
    status = "暂停中" if audio_player.is_paused else "播放中"
    current_time = audio_player.get_time()
    total_time = audio_player.get_length()
    volume = audio_player.get_volume()
    position = audio_player.get_position() * 100
    
    # 获取元数据
    metadata = audio_player.get_metadata()
    
    # 显示播放信息
    panel = Panel(
        f"[bold]文件名:[/bold] {current_item.server_filename}\n"
        f"[bold]路径:[/bold] {current_item.path}\n"
        f"[bold]大小:[/bold] {format_size(current_item.size)}\n"
        f"[bold]状态:[/bold] {status}\n"
        f"[bold]进度:[/bold] {format_time(current_time)} / {format_time(total_time)} ({position:.1f}%)\n"
        f"[bold]音量:[/bold] {volume}%",
        title="播放状态",
        border_style="cyan"
    )
    
    console.print(panel)
    
    # 显示元数据
    if metadata:
        metadata_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        metadata_table.add_column("标签", style="cyan")
        metadata_table.add_column("值", style="green")
        
        for key, value in metadata.items():
            metadata_table.add_row(str(key), str(value))
        
        console.print(Panel(metadata_table, title="音频元数据", border_style="cyan"))

if __name__ == "__main__":
    player()
