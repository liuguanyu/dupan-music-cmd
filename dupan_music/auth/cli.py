#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证命令行模块
"""

import click
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.utils.logger import LOGGER


console = Console()
auth_client = BaiduPanAuth()


@click.group("auth")
def auth():
    """认证相关命令"""
    pass


@auth.command("login")
def login():
    """登录百度网盘（使用授权码模式）"""
    if auth_client.is_authenticated():
        console.print(Panel("您已登录，无需重复登录", title="登录状态", border_style="green"))
        return
    
    # 使用授权码登录
    authorize_url = auth_client.get_authorize_url()
    console.print(Panel(f"请在浏览器中打开以下链接并授权：\n\n{authorize_url}", title="授权登录", border_style="blue"))
    
    # 尝试打开浏览器
    try:
        webbrowser.open(authorize_url)
    except Exception as e:
        LOGGER.error(f"打开浏览器失败: {e}")
    
    # 获取授权码
    code = click.prompt("请输入授权码")
    
    # 交换令牌
    console.print(Panel("正在登录，请稍候...", title="登录状态", border_style="blue"))
    success = auth_client.exchange_code_for_token(code)
    
    if success:
        console.print(Panel("登录成功", title="登录状态", border_style="green"))
    else:
        console.print(Panel("登录失败", title="登录状态", border_style="red"))


@auth.command("logout")
def logout():
    """退出登录"""
    if not auth_client.is_authenticated():
        console.print(Panel("您尚未登录", title="登录状态", border_style="yellow"))
        return
    
    # 确认退出
    if click.confirm("确定要退出登录吗？"):
        success = auth_client.logout()
        
        if success:
            console.print(Panel("已成功退出登录", title="登录状态", border_style="green"))
        else:
            console.print(Panel("退出登录失败", title="登录状态", border_style="red"))


@auth.command("status")
def status():
    """查看登录状态"""
    if auth_client.is_authenticated():
        # 获取用户信息
        user_info = auth_client.get_user_info()
        
        if user_info:
            # 创建表格
            table = Table(title="用户信息")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            # 添加用户信息
            table.add_row("用户名", user_info.get("baidu_name", "未知"))
            table.add_row("用户ID", str(user_info.get("uk", "未知")))
            table.add_row("会员类型", str(user_info.get("vip_type", "未知")))
            
            console.print(Panel.fit(table, title="登录状态", border_style="green"))
        else:
            console.print(Panel("已登录，但获取用户信息失败", title="登录状态", border_style="yellow"))
    else:
        console.print(Panel("未登录", title="登录状态", border_style="red"))


@auth.command("refresh")
def refresh():
    """刷新令牌"""
    if not auth_client.is_authenticated():
        console.print(Panel("您尚未登录", title="登录状态", border_style="yellow"))
        return
    
    console.print(Panel("正在刷新令牌，请稍候...", title="刷新令牌", border_style="blue"))
    success = auth_client.refresh_token()
    
    if success:
        console.print(Panel("刷新令牌成功", title="刷新令牌", border_style="green"))
    else:
        console.print(Panel("刷新令牌失败", title="刷新令牌", border_style="red"))


if __name__ == "__main__":
    auth()
