#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交互式shell实现
"""

import os
import sys
import shlex
from typing import List, Dict, Any, Optional, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, NestedCompleter, WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition
from rich.console import Console

from dupan_music import __version__
from dupan_music.auth.cli import auth
from dupan_music.api.cli import api
from dupan_music.playlist.cli import playlist
from dupan_music.player.cli import player
from dupan_music.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

# 定义命令样式
style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'command': 'ansigreen',
    'arg': 'ansiyellow',
    'completion': 'bg:#008888 #ffffff',
    'completion.cursor': '#44ffff',
    'completion.current': 'bg:#00aaaa #ffffff',
})

# 获取用户主目录
HOME_DIR = os.path.expanduser("~")
# 历史文件路径
HISTORY_FILE = os.path.join(HOME_DIR, ".dupan_music_history")


class DupanMusicCompleter(Completer):
    """百度盘音乐命令行自动补全"""

    def __init__(self):
        # 常用路径补全
        self.common_paths = [
            '/',
            '/音乐',
            '/视频',
            '/文档',
            '/图片',
            '/我的资源',
        ]
        
        # 常用参数补全
        self.common_args = {
            '--help': None,
            '--json': None,
            '--recursive': None,
            '--no-recursive': None,
            '--desc': None,
            '--asc': None,
        }
        
        # 命令补全字典
        self.commands = {
            'auth': {
                'login': None,
                'logout': None,
                'status': None,
                'refresh': None,
            },
            'api': {
                'list': {
                    '--path': None,
                    '-p': None,
                    '--order': None,
                    '-o': None,
                    '--desc': None,
                    '--asc': None,
                    '--limit': None,
                    '-l': None,
                    '--folder-only': None,
                    '--json': None,
                },
                'list-recursive': {
                    '--path': None,
                    '-p': None,
                    '--order': None,
                    '-o': None,
                    '--desc': None,
                    '--asc': None,
                    '--limit': None,
                    '-l': None,
                    '--json': None,
                },
                'search': {
                    '--path': None,
                    '-p': None,
                    '--recursive': None,
                    '--no-recursive': None,
                    '--page': None,
                    '--limit': None,
                    '-l': None,
                    '--json': None,
                },
                'info': {
                    '--with-link': None,
                    '--json': None,
                },
                'download-link': None,
                'audio': {
                    '--path': None,
                    '-p': None,
                    '--order': None,
                    '-o': None,
                    '--desc': None,
                    '--asc': None,
                    '--limit': None,
                    '-l': None,
                    '--json': None,
                },
                'user': None,
                'quota': None,
                'select-files': {
                    '--playlist': None,
                    '-p': None,
                    '--start-path': None,
                },
            },
            'playlist': {
                'list': {
                    '--json': None,
                },
                'create': {
                    '--description': None,
                    '-d': None,
                },
                'delete': None,
                'show': {
                    '--json': None,
                },
                'add': {
                    '--file-id': None,
                    '-f': None,
                    '--path': None,
                    '-p': None,
                },
                'remove': {
                    '--index': None,
                    '-i': None,
                    '--all': None,
                },
                'clear': None,
            },
            'player': {
                'play': {
                    '--playlist': None,
                    '-p': None,
                    '--index': None,
                    '-i': None,
                    '--shuffle': None,
                    '--repeat': None,
                    '--volume': None,
                    '-v': None,
                },
                'pause': None,
                'resume': None,
                'stop': None,
                'next': None,
                'prev': None,
                'volume': None,
                'status': None,
                'playlist': None,
            },
            'version': None,
            'help': None,
            'exit': None,
            'quit': None,
        }
        
        # 创建嵌套补全器
        self.nested_completer = NestedCompleter.from_nested_dict(self.commands)

        # 创建嵌套补全器
        self.nested_completer = NestedCompleter.from_nested_dict(self.commands)
        
        # 创建路径补全器
        self.path_completer = WordCompleter(self.common_paths, sentence=True)

    def get_completions(self, document, complete_event):
        """获取补全项"""
        text = document.text
        
        # 使用嵌套补全器获取补全项
        nested_completions = list(self.nested_completer.get_completions(document, complete_event))
        if nested_completions:
            for completion in nested_completions:
                yield completion
            return
            
        # 检查是否需要路径补全
        words = text.split()
        if len(words) >= 2:
            # 检查是否是需要路径的命令
            path_commands = [
                'api list', 'api list-recursive', 'api search', 'api audio',
                'playlist add-from-path'
            ]
            
            for cmd in path_commands:
                cmd_parts = cmd.split()
                if len(words) >= len(cmd_parts) and ' '.join(words[:len(cmd_parts)]) == cmd:
                    # 如果前面的命令匹配，尝试补全路径
                    path_text = words[-1] if words[-1].startswith('/') else '/'
                    path_document = document.document.Document(path_text)
                    for completion in self.path_completer.get_completions(path_document, complete_event):
                        yield completion
                    return


class InteractiveShell:
    """交互式shell"""

    def __init__(self):
        """初始化交互式shell"""
        # 创建历史记录
        self.history = FileHistory(HISTORY_FILE)
        
        # 创建补全器
        self.completer = DupanMusicCompleter()
        
        # 创建键绑定
        self.key_bindings = self._create_key_bindings()
        
        # 创建会话
        self.session = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            style=style,
            complete_in_thread=True,
            complete_while_typing=True,
            key_bindings=self.key_bindings,
            enable_history_search=True,  # 启用历史搜索
            enable_system_prompt=True,   # 启用系统提示
            complete_style='multi_column',  # 多列显示补全
        )
        
        # 命令历史索引
        self.history_index = 0
        
        # 命令映射
        self.commands = {
            'auth': auth,
            'api': api,
            'playlist': playlist,
            'player': player,
            'version': self.show_version,
            'help': self.show_help,
            'exit': self.exit_shell,
            'quit': self.exit_shell,
        }

    def show_version(self, *args, **kwargs):
        """显示版本信息"""
        from rich.panel import Panel
        console.print(Panel(f"百度盘音乐命令行播放器 v{__version__}"))

    def show_help(self, *args, **kwargs):
        """显示帮助信息"""
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        
        help_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        help_table.add_column("命令", style="cyan")
        help_table.add_column("描述", style="green")
        
        help_table.add_row("auth", "认证相关命令")
        help_table.add_row("api", "百度网盘API命令")
        help_table.add_row("playlist", "播放列表管理命令")
        help_table.add_row("player", "播放器控制命令")
        help_table.add_row("version", "显示版本信息")
        help_table.add_row("help", "显示帮助信息")
        help_table.add_row("exit/quit", "退出交互式shell")
        
        console.print(Panel(help_table, title="帮助信息"))
        console.print("\n使用 '[cyan]<命令> --help[/cyan]' 获取特定命令的帮助信息")

    def exit_shell(self, *args, **kwargs):
        """退出shell"""
        console.print("[bold green]感谢使用百度盘音乐命令行播放器，再见！[/bold green]")
        # 不使用sys.exit(0)，而是通过抛出异常来退出当前shell
        raise EOFError("退出shell")

    def parse_command(self, command_line: str) -> List[str]:
        """解析命令行"""
        try:
            return shlex.split(command_line)
        except ValueError as e:
            console.print(f"[red]命令解析错误: {str(e)}[/red]")
            return []

    def execute_command(self, command_args: List[str]) -> None:
        """执行命令"""
        if not command_args:
            return
        
        command = command_args[0]
        args = command_args[1:]
        
        if command in self.commands:
            try:
                # 保存原始参数
                orig_argv = sys.argv.copy()
                
                # 设置新参数
                sys.argv = [command] + args
                
                # 执行命令
                self.commands[command](args)
                
                # 恢复原始参数
                sys.argv = orig_argv
            except SystemExit:
                # 忽略Click的系统退出
                pass
            except EOFError:
                # 退出shell命令，向上传递异常
                raise
            except Exception as e:
                console.print(f"[red]命令执行错误: {str(e)}[/red]")
                logger.exception(f"命令执行错误: {str(e)}")
        else:
            console.print(f"[red]未知命令: {command}[/red]")
            console.print("使用 'help' 命令查看可用命令")

    def get_prompt_message(self) -> HTML:
        """获取提示符消息"""
        return HTML('<prompt>dupan-music</prompt> > ')

    def _create_key_bindings(self) -> KeyBindings:
        """创建键绑定"""
        kb = KeyBindings()
        
        # 上下方向键导航历史记录已经由prompt_toolkit默认实现
        
        # Ctrl+R 搜索历史记录
        @kb.add('c-r')
        def _(event):
            """搜索历史记录"""
            event.app.current_buffer.enable_history_search = True
        
        # Ctrl+Space 显示所有可能的补全
        @kb.add('c-space')
        def _(event):
            """显示所有可能的补全"""
            event.app.current_buffer.start_completion(select_first=False)
        
        # Ctrl+L 清屏
        @kb.add('c-l')
        def _(event):
            """清屏"""
            event.app.renderer.clear()
            
        # Tab键支持历史命令
        @kb.add('tab')
        def _(event):
            """Tab键支持历史命令"""
            buffer = event.app.current_buffer
            
            # 如果有补全项，使用默认的补全行为
            if buffer.complete_state:
                buffer.complete_next()
            # 如果没有补全项且当前输入为空，使用历史命令
            elif not buffer.text.strip():
                # 获取历史记录
                history = list(buffer.history.get_strings())
                if history:
                    # 使用最近的历史命令
                    buffer.text = history[-1]
            # 如果有文本但没有补全项，尝试开始补全
            else:
                buffer.start_completion(select_first=True)
        
        return kb
        
    def run(self) -> None:
        """运行交互式shell"""
        # 显示欢迎信息
        from rich.panel import Panel
        console.print(Panel(f"欢迎使用百度盘音乐命令行播放器 v{__version__}", 
                           border_style="green"))
        console.print("输入 'help' 获取帮助，输入 'exit' 或 'quit' 退出")
        console.print("提示: 按Tab键可以自动补全命令或使用最近的历史命令，方向键可以浏览历史记录")
        console.print("      Ctrl+R 搜索历史记录，Ctrl+Space 显示所有可能的补全")
        
        # 使用running标志控制shell运行
        running = True
        while running:
            try:
                # 获取用户输入
                command_line = self.session.prompt(
                    self.get_prompt_message(),
                    mouse_support=True,
                )
                
                # 跳过空命令
                command_line = command_line.strip()
                if not command_line:
                    continue
                
                # 解析并执行命令
                command_args = self.parse_command(command_line)
                self.execute_command(command_args)
                
            except KeyboardInterrupt:
                # Ctrl+C，继续循环
                continue
            except EOFError:
                # Ctrl+D 或 exit/quit 命令，退出shell
                running = False
                break
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
                logger.exception(f"Shell错误: {str(e)}")


def run_interactive_shell():
    """运行交互式shell"""
    shell = InteractiveShell()
    shell.run()


if __name__ == "__main__":
    run_interactive_shell()
