#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器命令行接口测试
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from dupan_music.player.cli import (
    player, get_player, play_playlist, play_single_file,
    pause_playback, stop_playback, next_track, prev_track,
    set_volume, show_status
)
from dupan_music.player.player import AudioPlayer
from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem


class TestPlayerCLI:
    """测试播放器命令行接口"""

    def setup_method(self):
        """测试前准备"""
        # 创建CLI运行器
        self.runner = CliRunner()
        
        # 创建模拟对象
        self.mock_auth = MagicMock(spec=BaiduPanAuth)
        self.mock_auth.is_authenticated.return_value = True
        
        self.mock_api = MagicMock(spec=BaiduPanAPI)
        
        self.mock_playlist_manager = MagicMock(spec=PlaylistManager)
        
        self.mock_player = MagicMock(spec=AudioPlayer)
        self.mock_player.playlist_manager = self.mock_playlist_manager
        self.mock_player.is_playing = True
        self.mock_player.is_paused = False
        
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
            ]
        )
        
        # 设置当前播放项
        self.mock_player.current_item = self.test_playlist.items[0]
        self.mock_player.current_index = 0
    
    @patch('dupan_music.player.cli.BaiduPanAuth')
    @patch('dupan_music.player.cli.BaiduPanAPI')
    @patch('dupan_music.player.cli.PlaylistManager')
    @patch('dupan_music.player.cli.AudioPlayer')
    def test_get_player_success(self, mock_audio_player_cls, mock_playlist_manager_cls, 
                               mock_api_cls, mock_auth_cls):
        """测试获取播放器实例（成功）"""
        # 设置模拟对象
        mock_auth = MagicMock()
        mock_auth.is_authenticated.return_value = True
        mock_auth_cls.return_value = mock_auth
        
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        
        mock_playlist_manager = MagicMock()
        mock_playlist_manager_cls.return_value = mock_playlist_manager
        
        mock_audio_player = MagicMock()
        mock_audio_player_cls.return_value = mock_audio_player
        
        # 调用获取播放器方法
        player = get_player()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_auth.is_authenticated.assert_called_once()
        mock_api_cls.assert_called_once_with(mock_auth)
        mock_playlist_manager_cls.assert_called_once_with(mock_api)
        mock_audio_player_cls.assert_called_once_with(mock_api, mock_playlist_manager)
        assert player == mock_audio_player
    
    @patch('dupan_music.player.cli.BaiduPanAuth')
    @patch('dupan_music.player.cli.sys.exit')
    def test_get_player_not_authenticated(self, mock_exit, mock_auth_cls):
        """测试获取播放器实例（未认证）"""
        # 设置模拟对象
        mock_auth = MagicMock()
        mock_auth.is_authenticated.return_value = False
        mock_auth_cls.return_value = mock_auth
        
        # 调用获取播放器方法
        get_player()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_auth.is_authenticated.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('dupan_music.player.cli.BaiduPanAuth')
    @patch('dupan_music.player.cli.sys.exit')
    def test_get_player_exception(self, mock_exit, mock_auth_cls):
        """测试获取播放器实例（异常）"""
        # 设置模拟对象
        mock_auth_cls.side_effect = Exception("测试异常")
        
        # 调用获取播放器方法
        get_player()
        
        # 验证结果
        mock_auth_cls.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('dupan_music.player.cli.get_player')
    def test_play_playlist_success(self, mock_get_player):
        """测试播放播放列表（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_player.play.return_value = True
        
        # 模拟键盘输入
        with patch('dupan_music.player.cli.os.name', 'posix'), \
             patch('dupan_music.player.cli.select.select', return_value=([], [], [])), \
             patch('dupan_music.player.cli.time.sleep', side_effect=KeyboardInterrupt):
            # 调用命令
            result = self.runner.invoke(player, ['play', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_player.set_playlist.assert_called_once_with(self.test_playlist)
        self.mock_player.play.assert_called_once_with(0)
    
    @patch('dupan_music.player.cli.get_player')
    def test_play_playlist_not_exist(self, mock_get_player):
        """测试播放播放列表（不存在）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_playlist_manager.get_playlist.return_value = None
        
        # 调用命令
        result = self.runner.invoke(player, ['play', 'nonexistent'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('nonexistent')
        self.mock_player.set_playlist.assert_not_called()
        self.mock_player.play.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_play_playlist_empty(self, mock_get_player):
        """测试播放播放列表（空列表）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        empty_playlist = Playlist(id="empty", name="空播放列表", items=[])
        self.mock_playlist_manager.get_playlist.return_value = empty_playlist
        
        # 调用命令
        result = self.runner.invoke(player, ['play', 'empty'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('empty')
        self.mock_player.set_playlist.assert_not_called()
        self.mock_player.play.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_play_playlist_invalid_index(self, mock_get_player):
        """测试播放播放列表（无效索引）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        
        # 调用命令
        result = self.runner.invoke(player, ['play', 'test_playlist', '--index', '10'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_player.set_playlist.assert_not_called()
        self.mock_player.play.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_play_playlist_play_failed(self, mock_get_player):
        """测试播放播放列表（播放失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_playlist_manager.get_playlist.return_value = self.test_playlist
        self.mock_player.play.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['play', 'test_playlist'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('test_playlist')
        self.mock_player.set_playlist.assert_called_once_with(self.test_playlist)
        self.mock_player.play.assert_called_once_with(0)
    
    @patch('dupan_music.player.cli.play_file')
    def test_play_single_file(self, mock_play_file):
        """测试播放单个文件"""
        # 调用命令
        result = self.runner.invoke(player, ['play-file', '12345'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_play_file.assert_called_once_with('12345')
    
    @patch('dupan_music.player.cli.get_player')
    def test_pause_playback_success(self, mock_get_player):
        """测试暂停播放（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.pause.return_value = True
        
        # 调用命令
        result = self.runner.invoke(player, ['pause'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.pause.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_pause_playback_not_playing(self, mock_get_player):
        """测试暂停播放（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['pause'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.pause.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_pause_playback_failed(self, mock_get_player):
        """测试暂停播放（失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.pause.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['pause'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.pause.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_stop_playback_success(self, mock_get_player):
        """测试停止播放（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.stop.return_value = True
        
        # 调用命令
        result = self.runner.invoke(player, ['stop'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.stop.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_stop_playback_not_playing(self, mock_get_player):
        """测试停止播放（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['stop'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.stop.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_stop_playback_failed(self, mock_get_player):
        """测试停止播放（失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.stop.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['stop'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.stop.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_next_track_success(self, mock_get_player):
        """测试下一曲（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.next.return_value = True
        
        # 调用命令
        result = self.runner.invoke(player, ['next'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.next.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_next_track_not_playing(self, mock_get_player):
        """测试下一曲（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['next'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.next.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_next_track_failed(self, mock_get_player):
        """测试下一曲（失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.next.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['next'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.next.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_prev_track_success(self, mock_get_player):
        """测试上一曲（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.prev.return_value = True
        
        # 调用命令
        result = self.runner.invoke(player, ['prev'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.prev.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_prev_track_not_playing(self, mock_get_player):
        """测试上一曲（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['prev'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.prev.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_prev_track_failed(self, mock_get_player):
        """测试上一曲（失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.prev.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['prev'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.prev.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_set_volume_success(self, mock_get_player):
        """测试设置音量（成功）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.set_volume.return_value = True
        
        # 调用命令
        result = self.runner.invoke(player, ['volume', '50'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.set_volume.assert_called_once_with(50)
    
    @patch('dupan_music.player.cli.get_player')
    def test_set_volume_not_playing(self, mock_get_player):
        """测试设置音量（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['volume', '50'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.set_volume.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_set_volume_failed(self, mock_get_player):
        """测试设置音量（失败）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.set_volume.return_value = False
        
        # 调用命令
        result = self.runner.invoke(player, ['volume', '50'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.set_volume.assert_called_once_with(50)
    
    @patch('dupan_music.player.cli.get_player')
    def test_set_volume_out_of_range(self, mock_get_player):
        """测试设置音量（超出范围）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.set_volume.return_value = True
        
        # 调用命令 - 超出上限
        result = self.runner.invoke(player, ['volume', '150'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.set_volume.assert_called_once_with(100)  # 应该被限制在100
        
        # 重置模拟对象
        mock_get_player.reset_mock()
        self.mock_player.set_volume.reset_mock()
        
        # 调用命令 - 超出下限
        result = self.runner.invoke(player, ['volume', '-10'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.set_volume.assert_called_once_with(0)  # 应该被限制在0
    
    @patch('dupan_music.player.cli.get_player')
    def test_show_status_playing(self, mock_get_player):
        """测试显示状态（播放中）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.get_time.return_value = 60
        self.mock_player.get_length.return_value = 180
        self.mock_player.get_volume.return_value = 80
        self.mock_player.get_position.return_value = 0.33
        self.mock_player.get_metadata.return_value = {
            "title": "测试标题",
            "artist": "测试艺术家",
            "album": "测试专辑"
        }
        
        # 调用命令
        result = self.runner.invoke(player, ['status'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.get_time.assert_called_once()
        self.mock_player.get_length.assert_called_once()
        self.mock_player.get_volume.assert_called_once()
        self.mock_player.get_position.assert_called_once()
        self.mock_player.get_metadata.assert_called_once()
    
    @patch('dupan_music.player.cli.get_player')
    def test_show_status_not_playing(self, mock_get_player):
        """测试显示状态（未播放）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.is_playing = False
        
        # 调用命令
        result = self.runner.invoke(player, ['status'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.get_time.assert_not_called()
        self.mock_player.get_length.assert_not_called()
    
    @patch('dupan_music.player.cli.get_player')
    def test_show_status_no_current_item(self, mock_get_player):
        """测试显示状态（无当前项）"""
        # 设置模拟对象
        mock_get_player.return_value = self.mock_player
        self.mock_player.current_item = None
        
        # 调用命令
        result = self.runner.invoke(player, ['status'])
        
        # 验证结果
        assert result.exit_code == 0
        mock_get_player.assert_called_once()
        self.mock_player.get_time.assert_not_called()
        self.mock_player.get_length.assert_not_called()
    
    def test_handle_key_press(self):
        """测试按键处理"""
        from dupan_music.player.cli import handle_key_press
        
        # 创建模拟播放器
        mock_player = MagicMock()
        
        # 测试空格键（暂停/恢复）
        handle_key_press(' ', mock_player)
        mock_player.pause.assert_called_once()
        mock_player.reset_mock()
        
        # 测试n键（下一曲）
        handle_key_press('n', mock_player)
        mock_player.next.assert_called_once()
        mock_player.reset_mock()
        
        # 测试p键（上一曲）
        handle_key_press('p', mock_player)
        mock_player.prev.assert_called_once()
        mock_player.reset_mock()
        
        # 测试+键（增加音量）
        mock_player.get_volume.return_value = 50
        handle_key_press('+', mock_player)
        mock_player.get_volume.assert_called_once()
        mock_player.set_volume.assert_called_once_with(55)
        mock_player.reset_mock()
        
        # 测试-键（减小音量）
        mock_player.get_volume.return_value = 50
        handle_key_press('-', mock_player)
        mock_player.get_volume.assert_called_once()
        mock_player.set_volume.assert_called_once_with(45)
        mock_player.reset_mock()
        
        # 测试q键（退出）
        handle_key_press('q', mock_player)
        mock_player.stop.assert_called_once()
