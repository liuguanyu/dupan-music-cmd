#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证模块测试
"""

import os
import json
import time
import pytest
from unittest.mock import patch, MagicMock, mock_open

from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.config.config import CONFIG


class TestBaiduPanAuth:
    """测试百度网盘认证类"""

    @patch('os.path.exists')
    @patch('dupan_music.auth.auth.read_file')
    def test_load_auth_info_with_file(self, mock_read_file, mock_exists):
        """测试加载认证信息（文件存在）"""
        # 模拟文件存在
        mock_exists.return_value = True
        
        # 模拟文件内容
        mock_auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        mock_read_file.return_value = json.dumps(mock_auth_info)
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 验证认证信息
        assert auth.auth_info["access_token"] == "test_access_token"
        assert auth.auth_info["refresh_token"] == "test_refresh_token"
        assert auth.auth_info["is_logged_in"] == True

    @patch('os.path.exists')
    def test_load_auth_info_without_file(self, mock_exists):
        """测试加载认证信息（文件不存在）"""
        # 模拟文件不存在
        mock_exists.return_value = False
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 验证认证信息
        assert auth.auth_info["access_token"] == ""
        assert auth.auth_info["refresh_token"] == ""
        assert auth.auth_info["is_logged_in"] == False

    @patch('dupan_music.auth.auth.write_file')
    def test_save_auth_info_success(self, mock_write_file):
        """测试保存认证信息（成功）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 保存认证信息
        result = auth._save_auth_info()
        
        # 验证结果
        assert result == True
        mock_write_file.assert_called_once()

    def test_save_auth_info_no_token(self):
        """测试保存认证信息（无令牌）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
            "scope": "",
            "is_logged_in": False
        }
        
        # 保存认证信息
        result = auth._save_auth_info()
        
        # 验证结果
        assert result == False

    @patch('dupan_music.auth.auth.BaiduPanAuth.refresh_token')
    def test_save_auth_info_expired(self, mock_refresh_token):
        """测试保存认证信息（令牌过期）"""
        # 模拟刷新令牌成功
        mock_refresh_token.return_value = True
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() - 3600,  # 已过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 保存认证信息
        result = auth._save_auth_info()
        
        # 验证结果
        assert result == True
        mock_refresh_token.assert_called_once()

    def test_is_authenticated_not_logged_in(self):
        """测试是否已认证（未登录）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
            "scope": "",
            "is_logged_in": False
        }
        
        # 验证是否已认证
        assert auth.is_authenticated() == False

    def test_is_authenticated_no_token(self):
        """测试是否已认证（无令牌）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
            "scope": "",
            "is_logged_in": True  # 已登录但无令牌
        }
        
        # 验证是否已认证
        assert auth.is_authenticated() == False

    @patch('dupan_music.auth.auth.BaiduPanAuth.refresh_token')
    def test_is_authenticated_expired(self, mock_refresh_token):
        """测试是否已认证（令牌过期）"""
        # 模拟刷新令牌成功
        mock_refresh_token.return_value = True
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() - 3600,  # 已过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 验证是否已认证
        assert auth.is_authenticated() == True
        mock_refresh_token.assert_called_once()

    def test_is_authenticated_valid(self):
        """测试是否已认证（有效）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,  # 未过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 验证是否已认证
        assert auth.is_authenticated() == True

    def test_get_authorize_url(self):
        """测试获取授权URL"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 获取授权URL
        url = auth.get_authorize_url()
        
        # 验证URL
        assert "client_id=" in url
        assert "response_type=code" in url
        assert "redirect_uri=" in url
        assert "scope=" in url

    @patch('requests.get')
    def test_exchange_code_for_token_success(self, mock_get):
        """测试交换授权码获取令牌（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "scope": "basic,netdisk"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 模拟保存认证信息
        auth._save_auth_info = MagicMock(return_value=True)
        
        # 交换授权码获取令牌
        result = auth.exchange_code_for_token("test_code")
        
        # 验证结果
        assert result == True
        assert auth.auth_info["access_token"] == "new_access_token"
        assert auth.auth_info["refresh_token"] == "new_refresh_token"
        assert auth.auth_info["is_logged_in"] == True
        auth._save_auth_info.assert_called_once()

    @patch('requests.get')
    def test_exchange_code_for_token_error(self, mock_get):
        """测试交换授权码获取令牌（错误）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "error": "invalid_code",
            "error_description": "Invalid authorization code"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 交换授权码获取令牌
        result = auth.exchange_code_for_token("invalid_code")
        
        # 验证结果
        assert result == False

    @patch('requests.get')
    def test_refresh_token_success(self, mock_get):
        """测试刷新令牌（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "scope": "basic,netdisk"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
            "expires_at": time.time() - 3600,  # 已过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 模拟保存认证信息
        auth._save_auth_info = MagicMock(return_value=True)
        
        # 刷新令牌
        result = auth.refresh_token()
        
        # 验证结果
        assert result == True
        assert auth.auth_info["access_token"] == "new_access_token"
        assert auth.auth_info["refresh_token"] == "new_refresh_token"
        assert auth.auth_info["is_logged_in"] == True
        auth._save_auth_info.assert_called_once()

    def test_refresh_token_no_refresh_token(self):
        """测试刷新令牌（无刷新令牌）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "old_access_token",
            "refresh_token": "",  # 无刷新令牌
            "expires_at": time.time() - 3600,  # 已过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 刷新令牌
        result = auth.refresh_token()
        
        # 验证结果
        assert result == False

    @patch('requests.get')
    def test_refresh_token_error(self, mock_get):
        """测试刷新令牌（错误）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "error": "invalid_refresh_token",
            "error_description": "Invalid refresh token"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "old_access_token",
            "refresh_token": "invalid_refresh_token",
            "expires_at": time.time() - 3600,  # 已过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 刷新令牌
        result = auth.refresh_token()
        
        # 验证结果
        assert result == False

    @patch('requests.get')
    def test_logout_success(self, mock_get):
        """测试退出登录（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 模拟保存认证信息
        auth._save_auth_info = MagicMock(return_value=True)
        
        # 退出登录
        result = auth.logout()
        
        # 验证结果
        assert result == True
        assert auth.auth_info["access_token"] == ""
        assert auth.auth_info["refresh_token"] == ""
        assert auth.auth_info["is_logged_in"] == False
        auth._save_auth_info.assert_called_once()

    def test_logout_no_token(self):
        """测试退出登录（无令牌）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
            "scope": "",
            "is_logged_in": False
        }
        
        # 退出登录
        result = auth.logout()
        
        # 验证结果
        assert result == True

    @patch('requests.get')
    def test_get_user_info_success(self, mock_get):
        """测试获取用户信息（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "errno": 0,
            "baidu_name": "test_user",
            "netdisk_name": "test_netdisk",
            "uk": 12345678,
            "vip_type": 1
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 模拟认证状态
        auth.is_authenticated = MagicMock(return_value=True)
        
        # 获取用户信息
        result = auth.get_user_info()
        
        # 验证结果
        assert result is not None
        assert result["errno"] == 0
        assert result["baidu_name"] == "test_user"
        assert result["netdisk_name"] == "test_netdisk"

    def test_get_user_info_not_authenticated(self):
        """测试获取用户信息（未认证）"""
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 模拟认证状态
        auth.is_authenticated = MagicMock(return_value=False)
        
        # 获取用户信息
        result = auth.get_user_info()
        
        # 验证结果
        assert result is None

    @patch('requests.get')
    def test_get_user_info_error(self, mock_get):
        """测试获取用户信息（错误）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "errno": 111,
            "error_msg": "Access token invalid or no longer valid"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设置认证信息
        auth.auth_info = {
            "access_token": "invalid_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() + 3600,
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        
        # 模拟认证状态
        auth.is_authenticated = MagicMock(return_value=True)
        
        # 获取用户信息
        result = auth.get_user_info()
        
        # 验证结果
        assert result is None

    @patch('requests.get')
    @patch('dupan_music.auth.auth.BaiduPanAuth._display_user_code')
    @patch('dupan_music.auth.auth.BaiduPanAuth._poll_device_code_status')
    def test_login_with_device_code_success(self, mock_poll, mock_display, mock_get):
        """测试设备码模式授权登录（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "test_user_code",
            "verification_url": "https://example.com/verify",
            "expires_in": 1800,
            "interval": 5
        }
        mock_get.return_value = mock_response
        
        # 模拟轮询状态
        mock_poll.return_value = True
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设备码模式授权登录
        result = auth.login_with_device_code()
        
        # 验证结果
        assert result == True
        mock_display.assert_called_once_with("test_user_code", "https://example.com/verify")
        mock_poll.assert_called_once_with("test_device_code")

    @patch('requests.get')
    def test_login_with_device_code_error(self, mock_get):
        """测试设备码模式授权登录（错误）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client"
        }
        mock_get.return_value = mock_response
        
        # 创建认证对象
        auth = BaiduPanAuth()
        
        # 设备码模式授权登录
        result = auth.login_with_device_code()
        
        # 验证结果
        assert result == False
