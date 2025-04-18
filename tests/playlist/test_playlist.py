#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放列表模块测试
"""

import os
import json
import time
import pytest
from unittest.mock import patch, MagicMock, mock_open, call

from dupan_music.playlist.playlist import PlaylistItem, Playlist, PlaylistManager


class TestPlaylistItem:
    """测试播放列表项"""

    def test_init(self):
        """测试初始化"""
        # 创建播放列表项
        item = PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024,
            category=1,
            isdir=0,
            local_mtime=1617235200,
            server_mtime=1617235200,
            md5="abcdef1234567890"
        )
        
        # 验证属性
        assert item.fs_id == 123456
        assert item.server_filename == "test.mp3"
        assert item.path == "/test/test.mp3"
        assert item.size == 1024
        assert item.category == 1
        assert item.isdir == 0
        assert item.local_mtime == 1617235200
        assert item.server_mtime == 1617235200
        assert item.md5 == "abcdef1234567890"
        assert item.add_time > 0  # 自动设置添加时间

    def test_from_api_result(self):
        """测试从API结果创建"""
        # API结果
        api_result = {
            "fs_id": 123456,
            "server_filename": "test.mp3",
            "path": "/test/test.mp3",
            "size": 1024,
            "category": 1,
            "isdir": 0,
            "local_mtime": 1617235200,
            "server_mtime": 1617235200,
            "md5": "abcdef1234567890"
        }
        
        # 创建播放列表项
        item = PlaylistItem.from_api_result(api_result)
        
        # 验证属性
        assert item.fs_id == 123456
        assert item.server_filename == "test.mp3"
        assert item.path == "/test/test.mp3"
        assert item.size == 1024
        assert item.category == 1
        assert item.isdir == 0
        assert item.local_mtime == 1617235200
        assert item.server_mtime == 1617235200
        assert item.md5 == "abcdef1234567890"
        assert item.add_time > 0

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建播放列表项
        item = PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024,
            category=1,
            isdir=0,
            local_mtime=1617235200,
            server_mtime=1617235200,
            md5="abcdef1234567890",
            add_time=1617235300
        )
        
        # 转换为字典
        data = item.to_dict()
        
        # 验证字典
        assert data["fs_id"] == 123456
        assert data["server_filename"] == "test.mp3"
        assert data["path"] == "/test/test.mp3"
        assert data["size"] == 1024
        assert data["category"] == 1
        assert data["isdir"] == 0
        assert data["local_mtime"] == 1617235200
        assert data["server_mtime"] == 1617235200
        assert data["md5"] == "abcdef1234567890"
        assert data["add_time"] == 1617235300

    def test_from_dict(self):
        """测试从字典创建"""
        # 字典数据
        data = {
            "fs_id": 123456,
            "server_filename": "test.mp3",
            "path": "/test/test.mp3",
            "size": 1024,
            "category": 1,
            "isdir": 0,
            "local_mtime": 1617235200,
            "server_mtime": 1617235200,
            "md5": "abcdef1234567890",
            "add_time": 1617235300
        }
        
        # 创建播放列表项
        item = PlaylistItem.from_dict(data)
        
        # 验证属性
        assert item.fs_id == 123456
        assert item.server_filename == "test.mp3"
        assert item.path == "/test/test.mp3"
        assert item.size == 1024
        assert item.category == 1
        assert item.isdir == 0
        assert item.local_mtime == 1617235200
        assert item.server_mtime == 1617235200
        assert item.md5 == "abcdef1234567890"
        assert item.add_time == 1617235300


class TestPlaylist:
    """测试播放列表"""

    def test_init(self):
        """测试初始化"""
        # 创建播放列表
        playlist = Playlist(
            name="测试播放列表",
            description="这是一个测试播放列表"
        )
        
        # 验证属性
        assert playlist.name == "测试播放列表"
        assert playlist.description == "这是一个测试播放列表"
        assert playlist.items == []
        assert playlist.create_time > 0
        assert playlist.update_time > 0

    def test_add_item(self):
        """测试添加播放列表项"""
        # 创建播放列表
        playlist = Playlist(name="测试播放列表")
        
        # 创建播放列表项
        item = PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024
        )
        
        # 添加播放列表项
        result = playlist.add_item(item)
        
        # 验证结果
        assert result is True
        assert len(playlist.items) == 1
        assert playlist.items[0].fs_id == 123456
        
        # 再次添加相同的项
        result = playlist.add_item(item)
        
        # 验证结果（不应该添加成功）
        assert result is False
        assert len(playlist.items) == 1

    def test_remove_item(self):
        """测试移除播放列表项"""
        # 创建播放列表
        playlist = Playlist(name="测试播放列表")
        
        # 创建播放列表项
        item1 = PlaylistItem(
            fs_id=123456,
            server_filename="test1.mp3",
            path="/test/test1.mp3",
            size=1024
        )
        item2 = PlaylistItem(
            fs_id=789012,
            server_filename="test2.mp3",
            path="/test/test2.mp3",
            size=2048
        )
        
        # 添加播放列表项
        playlist.add_item(item1)
        playlist.add_item(item2)
        
        # 移除播放列表项
        result = playlist.remove_item(123456)
        
        # 验证结果
        assert result is True
        assert len(playlist.items) == 1
        assert playlist.items[0].fs_id == 789012
        
        # 移除不存在的项
        result = playlist.remove_item(999999)
        
        # 验证结果
        assert result is False
        assert len(playlist.items) == 1

    def test_clear(self):
        """测试清空播放列表"""
        # 创建播放列表
        playlist = Playlist(name="测试播放列表")
        
        # 添加播放列表项
        playlist.add_item(PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024
        ))
        
        # 清空播放列表
        playlist.clear()
        
        # 验证结果
        assert len(playlist.items) == 0

    def test_sort_by(self):
        """测试排序播放列表"""
        # 创建播放列表
        playlist = Playlist(name="测试播放列表")
        
        # 添加播放列表项
        item1 = PlaylistItem(
            fs_id=123456,
            server_filename="b_test.mp3",
            path="/test/b_test.mp3",
            size=1024,
            server_mtime=1617235200,
            add_time=1617235300
        )
        item2 = PlaylistItem(
            fs_id=789012,
            server_filename="a_test.mp3",
            path="/test/a_test.mp3",
            size=2048,
            server_mtime=1617235100,
            add_time=1617235400
        )
        
        playlist.add_item(item1)
        playlist.add_item(item2)
        
        # 按名称排序（升序）
        playlist.sort_by("name")
        assert playlist.items[0].server_filename == "a_test.mp3"
        assert playlist.items[1].server_filename == "b_test.mp3"
        
        # 按名称排序（降序）
        playlist.sort_by("name", desc=True)
        assert playlist.items[0].server_filename == "b_test.mp3"
        assert playlist.items[1].server_filename == "a_test.mp3"
        
        # 按时间排序（升序）
        playlist.sort_by("time")
        assert playlist.items[0].server_mtime == 1617235100
        assert playlist.items[1].server_mtime == 1617235200
        
        # 按大小排序（降序）
        playlist.sort_by("size", desc=True)
        assert playlist.items[0].size == 2048
        assert playlist.items[1].size == 1024
        
        # 按添加时间排序（降序）
        playlist.sort_by("add_time", desc=True)
        assert playlist.items[0].add_time == 1617235400
        assert playlist.items[1].add_time == 1617235300

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建播放列表
        playlist = Playlist(
            name="测试播放列表",
            description="这是一个测试播放列表",
            create_time=1617235000,
            update_time=1617235100
        )
        
        # 添加播放列表项
        playlist.add_item(PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024,
            add_time=1617235200
        ))
        
        # 转换为字典
        data = playlist.to_dict()
        
        # 验证字典
        assert data["name"] == "测试播放列表"
        assert data["description"] == "这是一个测试播放列表"
        assert data["create_time"] == 1617235000
        assert data["update_time"] == 1617235100
        assert len(data["items"]) == 1
        assert data["items"][0]["fs_id"] == 123456
        assert data["items"][0]["server_filename"] == "test.mp3"
        assert data["items"][0]["add_time"] == 1617235200

    def test_from_dict(self):
        """测试从字典创建"""
        # 字典数据
        data = {
            "name": "测试播放列表",
            "description": "这是一个测试播放列表",
            "items": [
                {
                    "fs_id": 123456,
                    "server_filename": "test.mp3",
                    "path": "/test/test.mp3",
                    "size": 1024,
                    "add_time": 1617235200
                }
            ],
            "create_time": 1617235000,
            "update_time": 1617235100
        }
        
        # 创建播放列表
        playlist = Playlist.from_dict(data)
        
        # 验证属性
        assert playlist.name == "测试播放列表"
        assert playlist.description == "这是一个测试播放列表"
        assert playlist.create_time == 1617235000
        assert playlist.update_time == 1617235100
        assert len(playlist.items) == 1
        assert playlist.items[0].fs_id == 123456
        assert playlist.items[0].server_filename == "test.mp3"
        assert playlist.items[0].add_time == 1617235200


class TestPlaylistManager:
    """测试播放列表管理器"""

    @patch('dupan_music.playlist.playlist.ensure_dir')
    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.read_file')
    @patch('dupan_music.playlist.playlist.write_file')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_init(self, mock_home, mock_write_file, mock_read_file, mock_exists, mock_ensure_dir):
        """测试初始化"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = False
        mock_read_file.return_value = None
        mock_write_file.return_value = True
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 验证属性
        assert manager.playlists_dir == "/mock/home/.dupan_music/playlists"
        assert manager.api is None
        
        # 验证调用
        mock_ensure_dir.assert_called_once_with("/mock/home/.dupan_music/playlists")
        mock_write_file.assert_called_once()  # 创建最近播放列表

    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.os.listdir')
    @patch('dupan_music.playlist.playlist.read_file')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_get_all_playlists(self, mock_home, mock_read_file, mock_listdir, mock_exists):
        """测试获取所有播放列表"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = True
        mock_listdir.return_value = ["playlist1.json", "playlist2.json", "not_json.txt"]
        
        # 设置读取文件返回值
        mock_read_file.side_effect = [
            json.dumps({
                "name": "播放列表1",
                "description": "这是播放列表1",
                "items": []
            }),
            json.dumps({
                "name": "播放列表2",
                "description": "这是播放列表2",
                "items": []
            })
        ]
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 获取所有播放列表
        playlists = manager.get_all_playlists()
        
        # 验证结果
        assert len(playlists) == 2
        assert playlists[0].name == "播放列表1"
        assert playlists[1].name == "播放列表2"
        
        # 验证调用
        mock_read_file.assert_has_calls([
            call(os.path.join("/mock/home/.dupan_music/playlists", "playlist1.json")),
            call(os.path.join("/mock/home/.dupan_music/playlists", "playlist2.json"))
        ])

    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.read_file')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_get_playlist(self, mock_home, mock_read_file, mock_exists):
        """测试获取播放列表"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = True
        mock_read_file.return_value = json.dumps({
            "name": "测试播放列表",
            "description": "这是测试播放列表",
            "items": [
                {
                    "fs_id": 123456,
                    "server_filename": "test.mp3",
                    "path": "/test/test.mp3",
                    "size": 1024
                }
            ]
        })
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 获取播放列表
        playlist = manager.get_playlist("test")
        
        # 验证结果
        assert playlist.name == "测试播放列表"
        assert playlist.description == "这是测试播放列表"
        assert len(playlist.items) == 1
        assert playlist.items[0].fs_id == 123456
        
        # 验证调用
        mock_read_file.assert_called_once_with(
            os.path.join("/mock/home/.dupan_music/playlists", "test.json")
        )
        
        # 测试获取不存在的播放列表
        mock_exists.return_value = False
        playlist = manager.get_playlist("not_exist")
        assert playlist is None

    @patch('dupan_music.playlist.playlist.write_file')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_save_playlist(self, mock_home, mock_write_file):
        """测试保存播放列表"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_write_file.return_value = True
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 创建播放列表
        playlist = Playlist(
            name="测试播放列表",
            description="这是测试播放列表"
        )
        playlist.add_item(PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024
        ))
        
        # 保存播放列表
        result = manager.save_playlist(playlist, "test")
        
        # 验证结果
        assert result is True
        
        # 验证调用
        mock_write_file.assert_called_once()
        args, kwargs = mock_write_file.call_args
        assert args[0] == os.path.join("/mock/home/.dupan_music/playlists", "test.json")
        saved_data = json.loads(args[1])
        assert saved_data["name"] == "测试播放列表"
        assert saved_data["description"] == "这是测试播放列表"
        assert len(saved_data["items"]) == 1
        assert saved_data["items"][0]["fs_id"] == 123456

    @patch('dupan_music.playlist.playlist.os.remove')
    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_delete_playlist(self, mock_home, mock_exists, mock_remove):
        """测试删除播放列表"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = True
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 删除播放列表
        result = manager.delete_playlist("test")
        
        # 验证结果
        assert result is True
        
        # 验证调用
        mock_remove.assert_called_once_with(
            os.path.join("/mock/home/.dupan_music/playlists", "test.json")
        )
        
        # 测试删除不存在的播放列表
        mock_exists.return_value = False
        result = manager.delete_playlist("not_exist")
        assert result is False

    @patch('dupan_music.playlist.playlist.write_file')
    @patch('dupan_music.playlist.playlist.read_file')
    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_add_to_recent(self, mock_home, mock_exists, mock_read_file, mock_write_file):
        """测试添加到最近播放"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = True
        mock_read_file.return_value = json.dumps({
            "name": "最近播放",
            "description": "最近播放的音乐",
            "items": []
        })
        mock_write_file.return_value = True
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 创建播放列表项
        item = PlaylistItem(
            fs_id=123456,
            server_filename="test.mp3",
            path="/test/test.mp3",
            size=1024
        )
        
        # 添加到最近播放
        result = manager.add_to_recent(item)
        
        # 验证结果
        assert result is True
        
        # 验证调用
        mock_write_file.assert_called_once()
        args, kwargs = mock_write_file.call_args
        assert args[0] == os.path.join("/mock/home/.dupan_music/playlists", "recent.json")
        saved_data = json.loads(args[1])
        assert saved_data["name"] == "最近播放"
        assert saved_data["description"] == "最近播放的音乐"
        assert len(saved_data["items"]) == 1
        assert saved_data["items"][0]["fs_id"] == 123456

    @patch('dupan_music.playlist.playlist.read_file')
    @patch('dupan_music.playlist.playlist.os.path.exists')
    @patch('dupan_music.playlist.playlist.Path.home')
    def test_get_recent(self, mock_home, mock_exists, mock_read_file):
        """测试获取最近播放"""
        # 设置模拟对象
        mock_home.return_value = "/mock/home"
        mock_exists.return_value = True
        mock_read_file.return_value = json.dumps({
            "name": "最近播放",
            "description": "最近播放的音乐",
            "items": [
                {
                    "fs_id": 123456,
                    "server_filename": "test.mp3",
                    "path": "/test/test.mp3",
                    "size": 1024
                }
            ]
        })
        
        # 创建播放列表管理器
        manager = PlaylistManager()
        
        # 获取最近播放
        playlist = manager.get_recent()
        
        # 验证结果
        assert playlist.name == "最近播放"
        assert playlist.description == "最近播放的音乐"
        assert len(playlist.items) == 1
        assert playlist.items[0].fs_id == 123456
        
        # 验证调用
        mock_read_file.assert_called_once_with(
            os.path.join("/mock/home/.dupan_music/playlists", "recent.json")
        )
