#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API命令行接口测试
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from dupan_music.api.cli import (
    api, get_api_instance, list, list_recursive, search, info, 
    download_link, audio, user, quota, select_files
)
from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.playlist.playlist import PlaylistManager


class TestApiCLI:
    """测试API命令行接口"""

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
        self.mock_auth.is_authenticated.return_value = True
        
        # 创建模拟API对象
        self.mock_api = MagicMock(spec=BaiduPanAPI)

    @patch('dupan_music.api.cli.BaiduPanAuth')
    @patch('dupan_music.api.cli.BaiduPanAPI')
    def test_get_api_instance_success(self, mock_api_class, mock_auth_class):
        """测试获取API实例（成功）"""
        # 设置模拟对象
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = True
        mock_auth_class.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance
        
        # 调用函数
        api_instance = get_api_instance()
        
        # 验证结果
        assert api_instance == mock_api_instance
        mock_auth_class.assert_called_once()
        mock_auth_instance.is_authenticated.assert_called_once()
        mock_api_class.assert_called_once_with(mock_auth_instance)

    @patch('dupan_music.api.cli.BaiduPanAuth')
    @patch('dupan_music.api.cli.sys.exit')
    def test_get_api_instance_not_authenticated(self, mock_exit, mock_auth_class):
        """测试获取API实例（未认证）"""
        # 设置模拟对象
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = False
        mock_auth_class.return_value = mock_auth_instance
        
        # 调用函数
        with pytest.raises(SystemExit):
            get_api_instance()
        
        # 验证结果
        mock_auth_class.assert_called_once()
        mock_auth_instance.is_authenticated.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('dupan_music.api.cli.BaiduPanAuth')
    @patch('dupan_music.api.cli.sys.exit')
    def test_get_api_instance_exception(self, mock_exit, mock_auth_class):
        """测试获取API实例（异常）"""
        # 设置模拟对象
        mock_auth_class.side_effect = Exception("Auth error")
        
        # 调用函数
        with pytest.raises(SystemExit):
            get_api_instance()
        
        # 验证结果
        mock_auth_class.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('dupan_music.api.cli.get_api_instance')
    def test_list_command(self, mock_get_api):
        """测试list命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_list.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0,
                "server_mtime": 1617235200
            },
            {
                "fs_id": 789012,
                "path": "/test/folder1",
                "server_filename": "folder1",
                "size": 0,
                "isdir": 1,
                "server_mtime": 1617235200
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(list, ['--path', '/test', '--order', 'name', '--desc'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_file_list.assert_called_once_with(
            dir_path='/test',
            order='name',
            desc=True,
            limit=100,
            folder=0
        )
        # 验证输出包含文件名
        assert "file1.mp3" in result.output
        assert "folder1" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_list_command_json_output(self, mock_get_api):
        """测试list命令（JSON输出）"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_list.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(list, ['--path', '/test', '--json'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_file_list.assert_called_once()
        # 验证输出是JSON格式
        assert "123456" in result.output
        assert "file1.mp3" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_list_command_empty_result(self, mock_get_api):
        """测试list命令（空结果）"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_list.return_value = []
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(list, ['--path', '/empty'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_file_list.assert_called_once()
        # 验证输出提示没有文件
        assert "没有文件" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_list_command_exception(self, mock_get_api):
        """测试list命令（异常）"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_list.side_effect = Exception("API error")
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(list, ['--path', '/test'])
        
        # 验证结果
        assert result.exit_code == 0  # Click捕获异常后返回0
        mock_get_api.assert_called_once()
        mock_api.get_file_list.assert_called_once()
        # 验证输出包含错误信息
        assert "获取文件列表失败" in result.output
        assert "API error" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_list_recursive_command(self, mock_get_api):
        """测试list_recursive命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_list_recursive.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            },
            {
                "fs_id": 789012,
                "path": "/test/folder1/file2.mp3",
                "server_filename": "file2.mp3",
                "size": 2048,
                "isdir": 0
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(list_recursive, ['--path', '/test', '--order', 'time', '--asc'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_file_list_recursive.assert_called_once_with(
            dir_path='/test',
            order='time',
            desc=False,
            limit=100
        )
        # 验证输出包含文件名和路径
        assert "file1.mp3" in result.output
        assert "file2.mp3" in result.output
        assert "/test/folder1/file2.mp3" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_search_command(self, mock_get_api):
        """测试search命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.search_files.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(search, ['mp3', '--path', '/test', '--recursive'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.search_files.assert_called_once_with(
            key='mp3',
            dir_path='/test',
            recursion=1,
            page=1,
            num=100
        )
        # 验证输出包含文件名
        assert "file1.mp3" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_info_command(self, mock_get_api):
        """测试info命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_file_info.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "filename": "file1.mp3",
                "size": 1024,
                "isdir": 0,
                "md5": "abcdef1234567890",
                "server_ctime": 1617235200,
                "server_mtime": 1617235200,
                "dlink": "https://example.com/download/file1.mp3"
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(info, ['123456', '--with-link'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_file_info.assert_called_once_with([123456], dlink=1)
        # 验证输出包含文件信息
        assert "file1.mp3" in result.output
        assert "1024" in result.output or "1.0 KB" in result.output
        assert "abcdef1234567890" in result.output
        assert "https://example.com/download/file1.mp3" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_download_link_command(self, mock_get_api):
        """测试download_link命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_download_link.return_value = "https://example.com/real_download_link/file1.mp3"
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(download_link, ['123456'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_download_link.assert_called_once_with(123456)
        # 验证输出包含下载链接
        assert "https://example.com/real_download_link/file1.mp3" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_audio_command(self, mock_get_api):
        """测试audio命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_audio_files.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            },
            {
                "fs_id": 789012,
                "path": "/test/file2.flac",
                "server_filename": "file2.flac",
                "size": 2048,
                "isdir": 0
            }
        ]
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(audio, ['--path', '/test', '--order', 'name', '--desc'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_audio_files.assert_called_once_with(
            dir_path='/test',
            order='name',
            desc=True,
            limit=100
        )
        # 验证输出包含文件名
        assert "file1.mp3" in result.output
        assert "file2.flac" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_user_command(self, mock_get_api):
        """测试user命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_user_info.return_value = {
            "errno": 0,
            "baidu_name": "test_user",
            "netdisk_name": "test_netdisk",
            "uk": 12345678,
            "avatar_url": "https://example.com/avatar.jpg",
            "vip_type": 1
        }
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(user)
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_user_info.assert_called_once()
        # 验证输出包含用户信息
        assert "test_user" in result.output
        assert "test_netdisk" in result.output
        assert "12345678" in result.output
        assert "https://example.com/avatar.jpg" in result.output

    @patch('dupan_music.api.cli.get_api_instance')
    def test_quota_command(self, mock_get_api):
        """测试quota命令"""
        # 设置模拟对象
        mock_api = MagicMock()
        mock_api.get_quota.return_value = {
            "errno": 0,
            "total": 2199023255552,  # 2TB
            "used": 1099511627776,   # 1TB
            "free": 1099511627776    # 1TB
        }
        mock_get_api.return_value = mock_api
        
        # 调用命令
        result = self.runner.invoke(quota)
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_api.assert_called_once()
        mock_api.get_quota.assert_called_once()
        # 验证输出包含容量信息
        assert "总容量" in result.output
        assert "已使用" in result.output
        assert "剩余容量" in result.output
        assert "50.00%" in result.output  # 使用率

    @patch('dupan_music.api.cli.BaiduPanAuth')
    @patch('dupan_music.api.cli.BaiduPanAPI')
    @patch('dupan_music.api.cli.PlaylistManager')
    @patch('dupan_music.api.cli.Prompt.ask')
    @patch('dupan_music.api.cli.Confirm.ask')
    def test_select_files_with_playlist(self, mock_confirm, mock_prompt, mock_playlist_manager, mock_api_class, mock_auth_class):
        """测试select_files命令（指定播放列表）"""
        # 设置模拟对象
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = True
        mock_auth_class.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api_instance.get_file_list.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            },
            {
                "fs_id": 789012,
                "path": "/test/folder1",
                "server_filename": "folder1",
                "size": 0,
                "isdir": 1
            }
        ]
        mock_api_class.return_value = mock_api_instance
        
        mock_playlist_manager_instance = MagicMock()
        mock_playlist_manager_instance.get_playlist.return_value = {"name": "test_playlist", "description": "Test playlist"}
        mock_playlist_manager_instance.add_to_playlist.return_value = True
        mock_playlist_manager.return_value = mock_playlist_manager_instance
        
        # 模拟用户输入
        mock_prompt.side_effect = ["1", "d"]  # 选择文件1，然后完成
        mock_confirm.return_value = True
        
        # 调用命令
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(select_files, ['--playlist', 'test_playlist', '--start-path', '/test'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_auth_class.assert_called_once()
            mock_auth_instance.is_authenticated.assert_called_once()
            mock_api_class.assert_called_once()
            mock_playlist_manager.assert_called_once()
            mock_playlist_manager_instance.get_playlist.assert_called_once_with('test_playlist')
            mock_api_instance.get_file_list.assert_called_once_with(dir_path='/test')
            
            # 验证添加到播放列表
            mock_playlist_manager_instance.add_to_playlist.assert_called_once()
            args, kwargs = mock_playlist_manager_instance.add_to_playlist.call_args
            assert args[0] == 'test_playlist'
            assert args[1]["fs_id"] == 123456

    @patch('dupan_music.api.cli.BaiduPanAuth')
    @patch('dupan_music.api.cli.BaiduPanAPI')
    @patch('dupan_music.api.cli.PlaylistManager')
    @patch('dupan_music.api.cli.Prompt.ask')
    @patch('dupan_music.api.cli.Confirm.ask')
    def test_select_files_without_playlist(self, mock_confirm, mock_prompt, mock_playlist_manager, mock_api_class, mock_auth_class):
        """测试select_files命令（不指定播放列表）"""
        # 设置模拟对象
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = True
        mock_auth_class.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api_instance.get_file_list.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            }
        ]
        mock_api_class.return_value = mock_api_instance
        
        mock_playlist_manager_instance = MagicMock()
        mock_playlist_manager_instance.get_all_playlists.return_value = [
            MagicMock(name="test_playlist1", description="Test playlist 1"),
            MagicMock(name="test_playlist2", description="Test playlist 2")
        ]
        mock_playlist_manager_instance.add_to_playlist.return_value = True
        mock_playlist_manager.return_value = mock_playlist_manager_instance
        
        # 模拟用户输入
        mock_prompt.side_effect = ["1", "d", "1"]  # 选择文件1，完成，选择播放列表1
        mock_confirm.return_value = True
        
        # 调用命令
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(select_files, ['--start-path', '/test'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_auth_class.assert_called_once()
            mock_auth_instance.is_authenticated.assert_called_once()
            mock_api_class.assert_called_once()
            mock_playlist_manager.assert_called_once()
            mock_playlist_manager_instance.get_all_playlists.assert_called_once()
            mock_api_instance.get_file_list.assert_called_once_with(dir_path='/test')
            
            # 验证添加到播放列表
            mock_playlist_manager_instance.add_to_playlist.assert_called_once()
            args, kwargs = mock_playlist_manager_instance.add_to_playlist.call_args
            assert args[0] == "test_playlist1"
            assert args[1]["fs_id"] == 123456
