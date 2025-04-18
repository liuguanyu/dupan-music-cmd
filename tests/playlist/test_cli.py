#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放列表命令行接口测试
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from dupan_music.playlist.cli import (
    playlist, get_playlist_manager, list_playlists, show_playlist,
    create_playlist, delete_playlist, add_to_playlist, remove_from_playlist,
    clear_playlist, sort_playlist, show_recent, add_from_path, verify_playlist
)
from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem
from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth


class TestPlaylistCLI:
    """测试播放列表命令行接口"""

    def setup_method(self):
        """测试前准备"""
        # 创建CLI运行器
        self.runner = CliRunner()
        
        # 创建模拟对象
        self.mock_auth = MagicMock(spec=BaiduPanAuth)
        self.mock_auth.is_authenticated.return_value = True
        
        self.mock_api = MagicMock(spec=BaiduPanAPI)
        
        self.mock_playlist_manager = MagicMock(spec=PlaylistManager)
        
        # 创建测试播放列表
        self.test_playlist = Playlist(
            id="test_playlist",
            name="测试播放列表",
            description="测试描述",
            items=[
                PlaylistItem(
                    fs_id=12345,
                    server_filename="test1.mp3",
                    path="/test1.mp3",
                    size=1024,
                    local_ctime=1617235200,
                    local_mtime=1617235200,
                    server_ctime=1617235200,
                    server_mtime=1617235200,
                    is_dir=False,
                    category=1,
                    md5="test_md5_1"
                ),
                PlaylistItem(
                    fs_id=67890,
                    server_filename="test2.mp3",
                    path="/test2.mp3",
                    size=2048,
                    local_ctime=1617321600,
                    local_mtime=1617321600,
                    server_ctime=1617321600,
                    server_mtime=1617321600,
                    is_dir=False,
                    category=1,
                    md5="test_md5_2"
                )
            ],
            create_time=1617235200,
            update_time=1617321600
        )
        
        # 创建最近播放列表
        self.recent_playlist = Playlist(
            id=PlaylistManager.RECENT_PLAYLIST_NAME,
            name=PlaylistManager.RECENT_PLAYLIST_NAME,
            description="自动记录最近播放的音乐",
            items=[
                PlaylistItem(
                    fs_id=12345,
                    server_filename="recent1.mp3",
                    path="/recent1.mp3",
                    size=1024,
                    local_ctime=1617235200,
                    local_mtime=1617235200,
                    server_ctime=1617235200,
                    server_mtime=1617235200,
                    is_dir=False,
                    category=1,
                    md5="recent_md5_1"
                )
            ],
            create_time=1617235200,
            update_time=1617321600
        )
    
    @patch('dupan_music.playlist.cli.BaiduPanAuth')
    @patch('dupan_music.playlist.cli.BaiduPanAPI')
    @patch('dupan_music.playlist.cli.PlaylistManager')
    def test_get_playlist_manager_success(self, mock_playlist_manager_cls, 
                                         mock_api_cls, mock_auth_cls):
        """测试获取播放列表管理器实例（成功）"""
        # 设置模拟对象
        mock_auth = MagicMock()
        mock_auth.is_authenticated.return_value = True
        mock_auth_cls.return_value = mock_auth
        
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        
        mock_playlist_manager = MagicMock()
        mock_playlist_manager_cls.return_value = mock_playlist_manager
        
        # 调用获取播放列表管理器方法
        manager = get_playlist_manager()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_auth.is_authenticated.assert_called_once()
        mock_api_cls.assert_called_once_with(mock_auth)
        mock_playlist_manager_cls.assert_called_once_with(mock_api)
        assert manager == mock_playlist_manager
    
    @patch('dupan_music.playlist.cli.BaiduPanAuth')
    @patch('dupan_music.playlist.cli.PlaylistManager')
    def test_get_playlist_manager_not_authenticated(self, mock_playlist_manager_cls, mock_auth_cls):
        """测试获取播放列表管理器实例（未认证）"""
        # 设置模拟对象
        mock_auth = MagicMock()
        mock_auth.is_authenticated.return_value = False
        mock_auth_cls.return_value = mock_auth
        
        mock_playlist_manager = MagicMock()
        mock_playlist_manager_cls.return_value = mock_playlist_manager
        
        # 调用获取播放列表管理器方法
        manager = get_playlist_manager()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_auth.is_authenticated.assert_called_once()
        mock_playlist_manager_cls.assert_called_once_with()  # 无API参数
        assert manager == mock_playlist_manager
    
    @patch('dupan_music.playlist.cli.BaiduPanAuth')
    @patch('dupan_music.playlist.cli.sys.exit')
    def test_get_playlist_manager_exception(self, mock_exit, mock_auth_cls):
        """测试获取播放列表管理器实例（异常）"""
        # 设置模拟对象
        mock_auth_cls.side_effect = Exception("测试异常")
        
        # 调用获取播放列表管理器方法
        get_playlist_manager()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_list_playlists_success(self, mock_get_playlist_manager):
        """测试列出所有播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_all_playlists.return_value = [self.test_playlist, self.recent_playlist]
        
        # 调用命令
        result = self.runner.invoke(playlist, ['list'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_all_playlists.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_list_playlists_json(self, mock_get_playlist_manager):
        """测试列出所有播放列表（JSON格式）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_all_playlists.return_value = [self.test_playlist, self.recent_playlist]
        
        # 调用命令
        result = self.runner.invoke(playlist, ['list', '--json'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_all_playlists.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_list_playlists_empty(self, mock_get_playlist_manager):
        """测试列出所有播放列表（空）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_all_playlists.return_value = []
        
        # 调用命令
        result = self.runner.invoke(playlist, ['list'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_all_playlists.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_playlist_success(self, mock_get_playlist_manager):
        """测试显示播放列表内容（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['show', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_playlist_json(self, mock_get_playlist_manager):
        """测试显示播放列表内容（JSON格式）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['show', 'test_playlist', '--json'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_playlist_not_exist(self, mock_get_playlist_manager):
        """测试显示播放列表内容（不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['show', 'nonexistent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_playlist_empty(self, mock_get_playlist_manager):
        """测试显示播放列表内容（空列表）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        empty_playlist = Playlist(id="empty", name="空播放列表", items=[])
        self.mock_playlist_manager.get_playlist.return_value = empty_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['show', 'empty'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('empty')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_create_playlist_success(self, mock_get_playlist_manager):
        """测试创建新播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        self.mock_playlist_manager.create_playlist.return_value = self.test_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['create', 'new_playlist', '--description', '新播放列表描述'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('new_playlist')
        self.mock_playlist_manager.create_playlist.assert_called_once_with('new_playlist', '新播放列表描述')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_create_playlist_already_exists(self, mock_get_playlist_manager):
        """测试创建新播放列表（已存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['create', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.create_playlist.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_create_playlist_failed(self, mock_get_playlist_manager):
        """测试创建新播放列表（失败）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        self.mock_playlist_manager.create_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['create', 'failed_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('failed_playlist')
        self.mock_playlist_manager.create_playlist.assert_called_once_with('failed_playlist', '')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_delete_playlist_success(self, mock_get_playlist_manager):
        """测试删除播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.delete_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['delete', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.delete_playlist.assert_called_once_with('test_playlist')
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_delete_playlist_not_exist(self, mock_get_playlist_manager):
        """测试删除播放列表（不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['delete', 'nonexistent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.delete_playlist.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_add_to_playlist_success(self, mock_get_playlist_manager):
        """测试添加文件到播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.api.get_file_info.return_value = {
            "fs_id": 123456,
            "server_filename": "new_file.mp3",
            "path": "/new_file.mp3",
            "size": 1024,
            "category": 1,
            "isdir": 0
        }
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['add', 'test_playlist', '123456'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.api.get_file_info.assert_called_once_with('123456')
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_add_to_playlist_not_exist(self, mock_get_playlist_manager):
        """测试添加文件到播放列表（播放列表不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['add', 'nonexistent', '123456'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.api.get_file_info.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_remove_from_playlist_success(self, mock_get_playlist_manager):
        """测试从播放列表移除文件（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['remove', 'test_playlist', '12345'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_remove_from_playlist_not_exist(self, mock_get_playlist_manager):
        """测试从播放列表移除文件（播放列表不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['remove', 'nonexistent', '12345'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.save_playlist.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_clear_playlist_success(self, mock_get_playlist_manager):
        """测试清空播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['clear', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_clear_playlist_not_exist(self, mock_get_playlist_manager):
        """测试清空播放列表（播放列表不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['clear', 'nonexistent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.save_playlist.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_sort_playlist_success(self, mock_get_playlist_manager):
        """测试排序播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['sort', 'test_playlist', '--by', 'name'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_sort_playlist_not_exist(self, mock_get_playlist_manager):
        """测试排序播放列表（播放列表不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['sort', 'nonexistent', '--by', 'name'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.save_playlist.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_recent_success(self, mock_get_playlist_manager):
        """测试显示最近播放（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_recent.return_value = self.recent_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['recent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_recent.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_show_recent_json(self, mock_get_playlist_manager):
        """测试显示最近播放（JSON格式）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_recent.return_value = self.recent_playlist
        
        # 调用命令
        result = self.runner.invoke(playlist, ['recent', '--json'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_recent.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_add_from_path_success(self, mock_get_playlist_manager):
        """测试从路径添加文件到播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.api.list_files.return_value = [
            {
                "fs_id": 123456,
                "server_filename": "file1.mp3",
                "path": "/test/file1.mp3",
                "size": 1024,
                "category": 1,
                "isdir": 0
            },
            {
                "fs_id": 789012,
                "server_filename": "file2.mp3",
                "path": "/test/file2.mp3",
                "size": 2048,
                "category": 1,
                "isdir": 0
            }
        ]
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['add-path', 'test_playlist', '/test'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_playlist_manager.api.list_files.assert_called_once_with('/test')
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_add_from_path_not_exist(self, mock_get_playlist_manager):
        """测试从路径添加文件到播放列表（播放列表不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['add-path', 'nonexistent', '/test'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.api.list_files.assert_not_called()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_verify_playlist_success(self, mock_get_playlist_manager):
        """测试验证播放列表（成功）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_playlist_manager.api.get_file_info.side_effect = [
            {
                "fs_id": 12345,
                "server_filename": "test1.mp3",
                "path": "/test1.mp3",
                "size": 1024,
                "category": 1,
                "isdir": 0
            },
            {
                "fs_id": 67890,
                "server_filename": "test2.mp3",
                "path": "/test2.mp3",
                "size": 2048,
                "category": 1,
                "isdir": 0
            }
        ]
        self.mock_playlist_manager.save_playlist.return_value = True
        
        # 调用命令
        result = self.runner.invoke(playlist, ['verify', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        assert self.mock_playlist_manager.api.get_file_info.call_count == 2
        self.mock_playlist_manager.save_playlist.assert_called_once()
    
    @patch('dupan_music.playlist.cli.get_playlist_manager')
    def test_verify_playlist_not_exist(self, mock_get_playlist_manager):
        """测试验证播放列表（不存在）"""
        # 设置模拟对象
        mock_get_playlist_manager.return_value = self.mock_playlist_manager
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(playlist, ['verify', 'nonexistent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_playlist_manager.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_playlist_manager.api.get_file_info.assert_not_called()
