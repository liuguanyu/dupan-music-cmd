#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证命令行接口测试
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from dupan_music.auth.cli import auth, login, logout, status, refresh
from dupan_music.auth.auth import BaiduPanAuth


class TestAuthCLI:
    """测试认证命令行接口"""

    def setup_method(self):
        """测试前准备"""
        self.runner = CliRunner()
        
        # 创建模拟认证对象
        self.mock_auth = MagicMock(spec=BaiduPanAuth)
        self.mock_auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": 9999999999,  # 未过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.webbrowser.open')
    @patch('dupan_music.auth.cli.click.prompt')
    def test_login_command_success(self, mock_prompt, mock_webbrowser, mock_auth_client):
        """测试login命令（成功）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        mock_auth_client.get_authorize_url.return_value = "https://example.com/auth"
        mock_auth_client.exchange_code_for_token.return_value = True
        mock_prompt.return_value = "test_auth_code"
        
        # 调用命令
        result = self.runner.invoke(login)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_authorize_url.assert_called_once()
        mock_webbrowser.assert_called_once_with("https://example.com/auth")
        mock_prompt.assert_called_once()
        mock_auth_client.exchange_code_for_token.assert_called_once_with("test_auth_code")
        # 验证输出包含成功信息
        assert "登录成功" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_login_command_already_logged_in(self, mock_auth_client):
        """测试login命令（已登录）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        
        # 调用命令
        result = self.runner.invoke(login)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_authorize_url.assert_not_called()
        # 验证输出包含已登录信息
        assert "您已登录" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.webbrowser.open')
    @patch('dupan_music.auth.cli.click.prompt')
    def test_login_command_browser_error(self, mock_prompt, mock_webbrowser, mock_auth_client):
        """测试login命令（浏览器错误）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        mock_auth_client.get_authorize_url.return_value = "https://example.com/auth"
        mock_auth_client.exchange_code_for_token.return_value = True
        mock_prompt.return_value = "test_auth_code"
        mock_webbrowser.side_effect = Exception("Browser error")
        
        # 调用命令
        result = self.runner.invoke(login)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_authorize_url.assert_called_once()
        mock_webbrowser.assert_called_once_with("https://example.com/auth")
        mock_prompt.assert_called_once()
        mock_auth_client.exchange_code_for_token.assert_called_once_with("test_auth_code")
        # 验证输出包含成功信息
        assert "登录成功" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.webbrowser.open')
    @patch('dupan_music.auth.cli.click.prompt')
    def test_login_command_token_error(self, mock_prompt, mock_webbrowser, mock_auth_client):
        """测试login命令（令牌错误）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        mock_auth_client.get_authorize_url.return_value = "https://example.com/auth"
        mock_auth_client.exchange_code_for_token.return_value = False
        mock_prompt.return_value = "invalid_auth_code"
        
        # 调用命令
        result = self.runner.invoke(login)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_authorize_url.assert_called_once()
        mock_webbrowser.assert_called_once_with("https://example.com/auth")
        mock_prompt.assert_called_once()
        mock_auth_client.exchange_code_for_token.assert_called_once_with("invalid_auth_code")
        # 验证输出包含失败信息
        assert "登录失败" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.click.confirm')
    def test_logout_command_success(self, mock_confirm, mock_auth_client):
        """测试logout命令（成功）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.logout.return_value = True
        mock_confirm.return_value = True
        
        # 调用命令
        result = self.runner.invoke(logout)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_confirm.assert_called_once()
        mock_auth_client.logout.assert_called_once()
        # 验证输出包含成功信息
        assert "已成功退出登录" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.click.confirm')
    def test_logout_command_cancel(self, mock_confirm, mock_auth_client):
        """测试logout命令（取消）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_confirm.return_value = False
        
        # 调用命令
        result = self.runner.invoke(logout)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_confirm.assert_called_once()
        mock_auth_client.logout.assert_not_called()
        # 验证输出不包含成功信息
        assert "已成功退出登录" not in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_logout_command_not_logged_in(self, mock_auth_client):
        """测试logout命令（未登录）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        
        # 调用命令
        result = self.runner.invoke(logout)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.logout.assert_not_called()
        # 验证输出包含未登录信息
        assert "您尚未登录" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    @patch('dupan_music.auth.cli.click.confirm')
    def test_logout_command_error(self, mock_confirm, mock_auth_client):
        """测试logout命令（错误）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.logout.return_value = False
        mock_confirm.return_value = True
        
        # 调用命令
        result = self.runner.invoke(logout)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_confirm.assert_called_once()
        mock_auth_client.logout.assert_called_once()
        # 验证输出包含失败信息
        assert "退出登录失败" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_status_command_logged_in_with_info(self, mock_auth_client):
        """测试status命令（已登录，有用户信息）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.get_user_info.return_value = {
            "baidu_name": "test_user",
            "uk": 12345678,
            "vip_type": 1
        }
        
        # 调用命令
        result = self.runner.invoke(status)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_user_info.assert_called_once()
        # 验证输出包含用户信息
        assert "test_user" in result.output
        assert "12345678" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_status_command_logged_in_no_info(self, mock_auth_client):
        """测试status命令（已登录，无用户信息）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.get_user_info.return_value = None
        
        # 调用命令
        result = self.runner.invoke(status)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_user_info.assert_called_once()
        # 验证输出包含错误信息
        assert "已登录，但获取用户信息失败" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_status_command_not_logged_in(self, mock_auth_client):
        """测试status命令（未登录）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        
        # 调用命令
        result = self.runner.invoke(status)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.get_user_info.assert_not_called()
        # 验证输出包含未登录信息
        assert "未登录" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_refresh_command_success(self, mock_auth_client):
        """测试refresh命令（成功）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.refresh_token.return_value = True
        
        # 调用命令
        result = self.runner.invoke(refresh)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.refresh_token.assert_called_once()
        # 验证输出包含成功信息
        assert "刷新令牌成功" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_refresh_command_not_logged_in(self, mock_auth_client):
        """测试refresh命令（未登录）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = False
        
        # 调用命令
        result = self.runner.invoke(refresh)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.refresh_token.assert_not_called()
        # 验证输出包含未登录信息
        assert "您尚未登录" in result.output

    @patch('dupan_music.auth.cli.auth_client')
    def test_refresh_command_error(self, mock_auth_client):
        """测试refresh命令（错误）"""
        # 设置模拟对象
        mock_auth_client.is_authenticated.return_value = True
        mock_auth_client.refresh_token.return_value = False
        
        # 调用命令
        result = self.runner.invoke(refresh)
        
        # 验证结果
        assert result.exit_code == 0
        mock_auth_client.is_authenticated.assert_called_once()
        mock_auth_client.refresh_token.assert_called_once()
        # 验证输出包含失败信息
        assert "刷新令牌失败" in result.output
