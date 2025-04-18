#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
集成测试
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from dupan_music.config.config import Config
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.api.api import BaiduPanAPI
from dupan_music.playlist.playlist import PlaylistManager
from dupan_music.player.player import AudioPlayer


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 配置文件路径
        self.config_file = os.path.join(self.temp_dir.name, "config.json")
        self.auth_file = os.path.join(self.temp_dir.name, "auth.json")
        self.playlist_dir = os.path.join(self.temp_dir.name, "playlists")
        
        # 确保目录存在
        os.makedirs(self.playlist_dir, exist_ok=True)
        
        # 创建配置对象
        self.config = Config(self.config_file)
        self.config.set("storage.auth_file", self.auth_file)
        self.config.set("app_id", "test_app_id")
        self.config.set("app_key", "test_app_key")
        self.config.set("secret_key", "test_secret_key")
        self.config.save()
    
    def teardown_method(self):
        """测试后清理"""
        # 删除临时目录
        self.temp_dir.cleanup()
    
    @patch("requests.post")
    @patch("requests.get")
    def test_auth_api_integration(self, mock_get, mock_post):
        """测试认证和API模块集成"""
        # 模拟认证响应
        mock_post.return_value.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 2592000
        }
        mock_post.return_value.status_code = 200
        
        # 模拟API响应
        mock_get.return_value.json.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/test.mp3",
                    "server_filename": "test.mp3",
                    "size": 1024,
                    "local_ctime": 1617235200,
                    "local_mtime": 1617235200,
                    "isdir": 0
                }
            ]
        }
        mock_get.return_value.status_code = 200
        
        # 创建认证对象
        auth = BaiduPanAuth(self.config)
        
        # 模拟认证
        with patch.object(auth, "_get_device_id", return_value="test_device_id"):
            auth.set_token("test_access_token", "test_refresh_token", 2592000)
            
            # 验证认证状态
            assert auth.is_authenticated() is True
            assert auth.get_access_token() == "test_access_token"
            
            # 创建API对象
            api = BaiduPanAPI(auth)
            
            # 测试API调用
            file_list = api.list_files("/")
            
            # 验证结果
            assert len(file_list) == 1
            assert file_list[0]["path"] == "/test.mp3"
            assert file_list[0]["fs_id"] == 123456
    
    @patch("requests.get")
    def test_api_playlist_integration(self, mock_get):
        """测试API和播放列表模块集成"""
        # 模拟API响应
        mock_get.return_value.json.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/音乐/test.mp3",
                    "server_filename": "test.mp3",
                    "size": 1024,
                    "local_ctime": 1617235200,
                    "local_mtime": 1617235200,
                    "isdir": 0
                },
                {
                    "fs_id": 123457,
                    "path": "/音乐/test2.mp3",
                    "server_filename": "test2.mp3",
                    "size": 2048,
                    "local_ctime": 1617235300,
                    "local_mtime": 1617235300,
                    "isdir": 0
                }
            ]
        }
        mock_get.return_value.status_code = 200
        
        # 创建模拟认证对象
        auth = MagicMock()
        auth.is_authenticated.return_value = True
        auth.get_access_token.return_value = "test_access_token"
        
        # 创建API对象
        api = BaiduPanAPI(auth)
        
        # 创建播放列表管理器
        playlist_manager = PlaylistManager(api, playlist_dir=self.playlist_dir)
        
        # 创建播放列表
        playlist_manager.create_playlist("测试播放列表")
        
        # 添加文件到播放列表
        playlist_manager.add_files_to_playlist("测试播放列表", ["/音乐/test.mp3", "/音乐/test2.mp3"])
        
        # 获取播放列表
        playlist = playlist_manager.get_playlist("测试播放列表")
        
        # 验证结果
        assert len(playlist["files"]) == 2
        assert playlist["files"][0]["path"] == "/音乐/test.mp3"
        assert playlist["files"][1]["path"] == "/音乐/test2.mp3"
    
    @patch("dupan_music.player.player.vlc")
    def test_playlist_player_integration(self, mock_vlc):
        """测试播放列表和播放器模块集成"""
        # 模拟VLC实例
        mock_instance = MagicMock()
        mock_media = MagicMock()
        mock_player = MagicMock()
        
        mock_vlc.Instance.return_value = mock_instance
        mock_instance.media_new.return_value = mock_media
        mock_instance.media_player_new.return_value = mock_player
        
        # 创建模拟API对象
        api = MagicMock()
        api.get_download_link.return_value = "http://example.com/test.mp3"
        
        # 创建模拟播放列表管理器
        playlist_manager = MagicMock()
        playlist_manager.get_playlist.return_value = {
            "name": "测试播放列表",
            "files": [
                {
                    "fs_id": 123456,
                    "path": "/音乐/test.mp3",
                    "server_filename": "test.mp3",
                    "size": 1024
                },
                {
                    "fs_id": 123457,
                    "path": "/音乐/test2.mp3",
                    "server_filename": "test2.mp3",
                    "size": 2048
                }
            ]
        }
        
        # 创建播放器对象
        player = AudioPlayer(api, playlist_manager)
        
        # 加载播放列表
        player.load_playlist("测试播放列表")
        
        # 验证播放列表已加载
        assert player.current_playlist["name"] == "测试播放列表"
        assert len(player.current_playlist["files"]) == 2
        
        # 播放第一首歌
        with patch.object(player, "_check_file_validity", return_value=True):
            player.play()
            
            # 验证播放状态
            assert player.is_playing() is True
            assert player.current_index == 0
            
            # 播放下一首
            player.next()
            assert player.current_index == 1
            
            # 播放上一首
            player.previous()
            assert player.current_index == 0
    
    def test_config_auth_integration(self):
        """测试配置和认证模块集成"""
        # 创建配置对象
        config = Config(self.config_file)
        config.set("storage.auth_file", self.auth_file)
        config.set("app_id", "test_app_id")
        config.set("app_key", "test_app_key")
        config.set("secret_key", "test_secret_key")
        config.save()
        
        # 创建认证对象
        auth = BaiduPanAuth(config)
        
        # 验证配置已正确加载
        assert auth.app_id == "test_app_id"
        assert auth.app_key == "test_app_key"
        assert auth.secret_key == "test_secret_key"
        
        # 设置令牌
        with patch.object(auth, "_get_device_id", return_value="test_device_id"):
            auth.set_token("test_access_token", "test_refresh_token", 2592000)
            
            # 验证令牌已保存
            assert auth.get_access_token() == "test_access_token"
            assert auth.get_refresh_token() == "test_refresh_token"
            
            # 创建新的认证对象，验证令牌已从文件加载
            with patch.object(BaiduPanAuth, "_get_device_id", return_value="test_device_id"):
                new_auth = BaiduPanAuth(config)
                assert new_auth.get_access_token() == "test_access_token"
                assert new_auth.get_refresh_token() == "test_refresh_token"
