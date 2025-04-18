#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器模块测试
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock, call

from dupan_music.player.player import AudioPlayer
from dupan_music.api.api import BaiduPanAPI
from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem


class TestAudioPlayer:
    """测试音频播放器"""

    def setup_method(self):
        """测试前准备"""
        # 创建模拟API
        self.mock_api = MagicMock(spec=BaiduPanAPI)
        self.mock_api.get_download_link.return_value = "https://example.com/test.mp3"
        
        # 创建模拟播放列表管理器
        self.mock_playlist_manager = MagicMock(spec=PlaylistManager)
        self.mock_playlist_manager.check_file_validity.return_value = True
        
        # 创建测试播放列表
        self.test_playlist = Playlist(
            id="test_playlist",
            name="测试播放列表",
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
        
        # 模拟VLC实例和播放器
        self.mock_vlc_instance = MagicMock()
        self.mock_vlc_player = MagicMock()
        self.mock_vlc_media = MagicMock()
        
        # 模拟VLC状态
        self.mock_vlc_state = MagicMock()
        self.mock_vlc_state.Ended = 6
        
        # 创建播放器实例
        with patch('dupan_music.player.player.vlc.Instance', return_value=self.mock_vlc_instance), \
             patch('dupan_music.player.player.vlc.State', self.mock_vlc_state):
            self.mock_vlc_instance.media_player_new.return_value = self.mock_vlc_player
            self.mock_vlc_instance.media_new.return_value = self.mock_vlc_media
            
            self.player = AudioPlayer(
                api=self.mock_api,
                playlist_manager=self.mock_playlist_manager
            )
    
    @patch('dupan_music.player.player.os.path.exists')
    @patch('dupan_music.player.player.os.remove')
    def test_clean_temp_file(self, mock_remove, mock_exists):
        """测试清理临时文件"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 设置临时文件
        self.player.temp_file = "/tmp/test.mp3"
        
        # 调用清理方法
        self.player._clean_temp_file()
        
        # 验证结果
        mock_exists.assert_called_once_with("/tmp/test.mp3")
        mock_remove.assert_called_once_with("/tmp/test.mp3")
        assert self.player.temp_file is None
    
    @patch('dupan_music.player.player.requests.get')
    @patch('dupan_music.player.player.get_file_extension')
    @patch('dupan_music.player.player.get_temp_file')
    def test_download_file_success(self, mock_get_temp_file, mock_get_file_extension, mock_requests_get):
        """测试下载文件（成功）"""
        # 设置模拟对象
        mock_get_file_extension.return_value = ".mp3"
        mock_get_temp_file.return_value = "/tmp/test.mp3"
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b"test_data"]
        mock_requests_get.return_value = mock_response
        
        # 创建测试项
        test_item = PlaylistItem(
            fs_id=12345,
            server_filename="test.mp3",
            path="/test.mp3",
            size=1024,
            local_ctime=1617235200,
            local_mtime=1617235200,
            server_ctime=1617235200,
            server_mtime=1617235200,
            is_dir=False,
            category=1,
            md5="test_md5"
        )
        
        # 模拟文件打开
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)
        
        # 调用下载方法
        with patch('builtins.open', mock_open):
            result = self.player._download_file(test_item)
        
        # 验证结果
        self.mock_api.get_download_link.assert_called_once_with(12345)
        mock_requests_get.assert_called_once_with("https://example.com/test.mp3", stream=True)
        mock_response.raise_for_status.assert_called_once()
        mock_response.iter_content.assert_called_once_with(chunk_size=8192)
        mock_open.assert_called_once_with("/tmp/test.mp3", 'wb')
        mock_file.__enter__().write.assert_called_once_with(b"test_data")
        assert result == "/tmp/test.mp3"
    
    @patch('dupan_music.player.player.requests.get')
    def test_download_file_error(self, mock_requests_get):
        """测试下载文件（错误）"""
        # 设置模拟对象
        mock_requests_get.side_effect = Exception("Download error")
        
        # 创建测试项
        test_item = PlaylistItem(
            fs_id=12345,
            server_filename="test.mp3",
            path="/test.mp3",
            size=1024,
            local_ctime=1617235200,
            local_mtime=1617235200,
            server_ctime=1617235200,
            server_mtime=1617235200,
            is_dir=False,
            category=1,
            md5="test_md5"
        )
        
        # 调用下载方法
        result = self.player._download_file(test_item)
        
        # 验证结果
        self.mock_api.get_download_link.assert_called_once_with(12345)
        mock_requests_get.assert_called_once_with("https://example.com/test.mp3", stream=True)
        assert result is None
    
    def test_check_file_validity(self):
        """测试检查文件有效性"""
        # 创建测试项
        test_item = PlaylistItem(
            fs_id=12345,
            server_filename="test.mp3",
            path="/test.mp3",
            size=1024,
            local_ctime=1617235200,
            local_mtime=1617235200,
            server_ctime=1617235200,
            server_mtime=1617235200,
            is_dir=False,
            category=1,
            md5="test_md5"
        )
        
        # 调用检查方法
        result = self.player._check_file_validity(test_item)
        
        # 验证结果
        self.mock_playlist_manager.check_file_validity.assert_called_once_with(12345)
        assert result is True
    
    def test_refresh_file(self):
        """测试刷新文件信息"""
        # 设置模拟对象
        self.mock_playlist_manager.refresh_file.return_value = {
            "fs_id": 12345,
            "server_filename": "test_refreshed.mp3",
            "path": "/test_refreshed.mp3",
            "size": 2048,
            "local_ctime": 1617235200,
            "local_mtime": 1617235200,
            "server_ctime": 1617235200,
            "server_mtime": 1617235200,
            "isdir": 0,
            "category": 1,
            "md5": "test_md5_refreshed"
        }
        
        # 创建测试项
        test_item = PlaylistItem(
            fs_id=12345,
            server_filename="test.mp3",
            path="/test.mp3",
            size=1024,
            local_ctime=1617235200,
            local_mtime=1617235200,
            server_ctime=1617235200,
            server_mtime=1617235200,
            is_dir=False,
            category=1,
            md5="test_md5"
        )
        
        # 调用刷新方法
        result = self.player._refresh_file(test_item)
        
        # 验证结果
        self.mock_playlist_manager.refresh_file.assert_called_once_with(12345)
        assert result is not None
        assert result.fs_id == 12345
        assert result.server_filename == "test_refreshed.mp3"
        assert result.size == 2048
        assert result.md5 == "test_md5_refreshed"
    
    def test_set_playlist(self):
        """测试设置播放列表"""
        # 调用设置方法
        result = self.player.set_playlist(self.test_playlist)
        
        # 验证结果
        assert result is True
        assert self.player.current_playlist == self.test_playlist
        assert self.player.current_item is None
        assert self.player.current_index == -1
    
    @patch('dupan_music.player.player.threading.Thread')
    @patch('dupan_music.player.player.os.path.exists')
    def test_play_success(self, mock_exists, mock_thread):
        """测试播放（成功）"""
        # 设置模拟对象
        mock_exists.return_value = True
        self.mock_vlc_player.play.return_value = 0
        
        # 模拟下载文件
        with patch.object(self.player, '_download_file', return_value="/tmp/test.mp3"):
            # 设置播放列表
            self.player.set_playlist(self.test_playlist)
            
            # 调用播放方法
            result = self.player.play(0)
        
        # 验证结果
        assert result is True
        assert self.player.current_index == 0
        assert self.player.current_item == self.test_playlist.items[0]
        assert self.player.is_playing is True
        assert self.player.is_paused is False
        assert self.player.temp_file == "/tmp/test.mp3"
        
        self.mock_vlc_instance.media_new.assert_called_once_with("/tmp/test.mp3")
        self.mock_vlc_player.set_media.assert_called_once_with(self.mock_vlc_media)
        self.mock_vlc_player.play.assert_called_once()
        self.mock_playlist_manager.add_to_recent_playlist.assert_called_once()
    
    def test_play_invalid_index(self):
        """测试播放（无效索引）"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        
        # 调用播放方法（无效索引）
        result = self.player.play(10)
        
        # 验证结果
        assert result is False
        assert self.player.current_index == -1
        assert self.player.current_item is None
        assert self.player.is_playing is False
    
    @patch('dupan_music.player.player.os.path.exists')
    def test_play_download_error(self, mock_exists):
        """测试播放（下载错误）"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 模拟下载文件失败
        with patch.object(self.player, '_download_file', return_value=None):
            # 设置播放列表
            self.player.set_playlist(self.test_playlist)
            
            # 调用播放方法
            result = self.player.play(0)
        
        # 验证结果
        assert result is False
        assert self.player.current_index == 0
        assert self.player.current_item == self.test_playlist.items[0]
        assert self.player.is_playing is False
    
    def test_pause_resume(self):
        """测试暂停/恢复"""
        # 设置播放状态
        self.player.is_playing = True
        self.player.is_paused = False
        self.player.current_item = self.test_playlist.items[0]
        
        # 调用暂停方法
        result = self.player.pause()
        
        # 验证结果
        assert result is True
        assert self.player.is_paused is True
        self.mock_vlc_player.pause.assert_called_once()
        
        # 调用恢复方法
        result = self.player.pause()
        
        # 验证结果
        assert result is True
        assert self.player.is_paused is False
        self.mock_vlc_player.play.assert_called_once()
    
    def test_pause_not_playing(self):
        """测试暂停（未播放）"""
        # 设置播放状态
        self.player.is_playing = False
        
        # 调用暂停方法
        result = self.player.pause()
        
        # 验证结果
        assert result is False
    
    @patch('dupan_music.player.player.os.path.exists')
    @patch('dupan_music.player.player.os.remove')
    def test_stop(self, mock_remove, mock_exists):
        """测试停止"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 设置播放状态
        self.player.is_playing = True
        self.player.is_paused = False
        self.player.temp_file = "/tmp/test.mp3"
        
        # 调用停止方法
        result = self.player.stop()
        
        # 验证结果
        assert result is True
        assert self.player.is_playing is False
        assert self.player.is_paused is False
        self.mock_vlc_player.stop.assert_called_once()
        mock_exists.assert_called_once_with("/tmp/test.mp3")
        mock_remove.assert_called_once_with("/tmp/test.mp3")
    
    def test_next(self):
        """测试下一曲"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        self.player.current_index = 0
        
        # 模拟播放方法
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            # 调用下一曲方法
            result = self.player.next()
            
            # 验证结果
            assert result is True
            mock_play.assert_called_once_with(1)
    
    def test_next_loop(self):
        """测试下一曲（循环）"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        self.player.current_index = 1  # 最后一项
        
        # 模拟播放方法
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            # 调用下一曲方法
            result = self.player.next()
            
            # 验证结果
            assert result is True
            mock_play.assert_called_once_with(0)  # 应该回到第一项
    
    def test_prev(self):
        """测试上一曲"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        self.player.current_index = 1
        
        # 模拟播放方法
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            # 调用上一曲方法
            result = self.player.prev()
            
            # 验证结果
            assert result is True
            mock_play.assert_called_once_with(0)
    
    def test_prev_loop(self):
        """测试上一曲（循环）"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        self.player.current_index = 0  # 第一项
        
        # 模拟播放方法
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            # 调用上一曲方法
            result = self.player.prev()
            
            # 验证结果
            assert result is True
            mock_play.assert_called_once_with(1)  # 应该跳到最后一项
    
    def test_play_modes(self):
        """测试播放模式"""
        # 设置播放列表
        self.player.set_playlist(self.test_playlist)
        self.player.current_index = 1  # 最后一项
        
        # 测试顺序播放模式
        self.player.set_play_mode(self.player.PlayMode.SEQUENTIAL)
        assert self.player.get_play_mode() == "sequential"
        
        # 在顺序播放模式下，最后一首歌的下一首应该返回False
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            result = self.player.next()
            assert result is False  # 顺序播放模式下，最后一首的下一首应该返回False
            mock_play.assert_not_called()  # 不应该调用play方法
        
        # 测试循环播放模式
        self.player.set_play_mode(self.player.PlayMode.LOOP)
        assert self.player.get_play_mode() == "loop"
        
        # 在循环播放模式下，最后一首歌的下一首应该是第一首
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            result = self.player.next()
            assert result is True
            mock_play.assert_called_once_with(0)  # 应该回到第一项
        
        # 测试随机播放模式
        self.player.set_play_mode(self.player.PlayMode.RANDOM)
        assert self.player.get_play_mode() == "random"
        
        # 在随机播放模式下，应该随机选择一首歌
        with patch.object(self.player, 'play', return_value=True) as mock_play:
            with patch('random.randint', return_value=0) as mock_randint:  # 模拟随机数
                result = self.player.next()
                assert result is True
                mock_play.assert_called_once_with(0)  # 应该播放随机选择的歌曲
                mock_randint.assert_called_once_with(0, 1)  # 应该在0-1之间随机选择
    
    @patch('dupan_music.player.player.os.path.exists')
    def test_play_random_mode(self, mock_exists):
        """测试随机播放模式"""
        # 设置模拟对象
        mock_exists.return_value = True
        self.mock_vlc_player.play.return_value = 0
        
        # 设置播放列表和随机播放模式
        self.player.set_playlist(self.test_playlist)
        self.player.set_play_mode(self.player.PlayMode.RANDOM)
        
        # 测试场景1：首次播放（使用默认索引0）
        with patch('random.randint', return_value=1) as mock_randint:
            with patch.object(self.player, '_download_file', return_value="/tmp/test.mp3"):
                # 调用播放方法（使用默认索引0）
                result = self.player.play()
                
                # 验证结果
                assert result is True
                # 应该随机选择索引1而不是默认的0
                assert self.player.current_index == 1
                assert self.player.current_item == self.test_playlist.items[1]
                mock_randint.assert_called_once_with(0, 1)  # 应该在0-1之间随机选择
        
        # 测试场景2：指定非默认索引
        self.player.current_index = -1  # 重置当前索引
        with patch('random.randint', return_value=0) as mock_randint:
            with patch.object(self.player, '_download_file', return_value="/tmp/test.mp3"):
                # 调用播放方法（指定索引1）
                result = self.player.play(1)
                
                # 验证结果
                assert result is True
                # 即使指定了索引1，在随机播放模式下也应该随机选择索引0
                assert self.player.current_index == 0
                assert self.player.current_item == self.test_playlist.items[0]
                mock_randint.assert_called_once_with(0, 1)  # 应该在0-1之间随机选择
        
        # 测试场景3：非首次播放
        self.player.current_index = 0  # 设置当前索引为0
        with patch('random.randint', return_value=1) as mock_randint:
            with patch.object(self.player, '_download_file', return_value="/tmp/test.mp3"):
                # 调用播放方法（使用默认索引0）
                result = self.player.play()
                
                # 验证结果
                assert result is True
                # 即使不是首次播放，在随机播放模式下也应该随机选择索引1
                assert self.player.current_index == 1
                assert self.player.current_item == self.test_playlist.items[1]
                mock_randint.assert_called_once_with(0, 1)  # 应该在0-1之间随机选择
    
    def test_volume_control(self):
        """测试音量控制"""
        # 调用设置音量方法
        result = self.player.set_volume(50)
        
        # 验证结果
        assert result is True
        self.mock_vlc_player.audio_set_volume.assert_called_once_with(50)
        
        # 设置模拟对象
        self.mock_vlc_player.audio_get_volume.return_value = 50
        
        # 调用获取音量方法
        volume = self.player.get_volume()
        
        # 验证结果
        assert volume == 50
        self.mock_vlc_player.audio_get_volume.assert_called_once()
    
    def test_position_control(self):
        """测试位置控制"""
        # 设置播放状态
        self.player.is_playing = True
        
        # 设置模拟对象
        self.mock_vlc_player.get_position.return_value = 0.5
        
        # 调用获取位置方法
        position = self.player.get_position()
        
        # 验证结果
        assert position == 0.5
        self.mock_vlc_player.get_position.assert_called_once()
        
        # 调用设置位置方法
        result = self.player.set_position(0.75)
        
        # 验证结果
        assert result is True
        self.mock_vlc_player.set_position.assert_called_once_with(0.75)
    
    def test_time_and_length(self):
        """测试时间和长度"""
        # 设置播放状态
        self.player.is_playing = True
        self.player.media = self.mock_vlc_media
        
        # 设置模拟对象
        self.mock_vlc_player.get_time.return_value = 60000  # 60秒
        self.mock_vlc_media.get_duration.return_value = 180000  # 180秒
        
        # 调用获取时间方法
        time_ms = self.player.get_time()
        
        # 验证结果
        assert time_ms == 60000
        self.mock_vlc_player.get_time.assert_called_once()
        
        # 调用获取长度方法
        length_ms = self.player.get_length()
        
        # 验证结果
        assert length_ms == 180000
        self.mock_vlc_media.get_duration.assert_called_once()
    
    @patch('dupan_music.player.player.MutagenFile')
    def test_get_metadata(self, mock_mutagen_file):
        """测试获取元数据"""
        # 设置播放状态
        self.player.temp_file = "/tmp/test.mp3"
        
        # 设置模拟对象
        mock_exists = MagicMock(return_value=True)
        mock_audio_file = MagicMock()
        mock_audio_file.items.return_value = [
            ('title', ['Test Title']),
            ('artist', ['Test Artist']),
            ('album', 'Test Album')
        ]
        mock_mutagen_file.return_value = mock_audio_file
        
        # 调用获取元数据方法
        with patch('dupan_music.player.player.os.path.exists', mock_exists):
            metadata = self.player.get_metadata()
        
        # 验证结果
        mock_exists.assert_called_once_with("/tmp/test.mp3")
        mock_mutagen_file.assert_called_once_with("/tmp/test.mp3")
        assert metadata == {'title': 'Test Title', 'artist': 'Test Artist', 'album': 'Test Album'}
    
    @patch('dupan_music.player.player.AudioSegment')
    @patch('dupan_music.player.player.get_temp_file')
    def test_convert_format(self, mock_get_temp_file, mock_audio_segment):
        """测试转换格式"""
        # 设置模拟对象
        mock_exists = MagicMock(return_value=True)
        mock_audio = MagicMock()
        mock_audio_segment.from_file.return_value = mock_audio
        mock_get_temp_file.return_value = "/tmp/output.mp3"
        
        # 调用转换格式方法
        with patch('dupan_music.player.player.os.path.exists', mock_exists):
            result = self.player.convert_format("/tmp/input.m4a", "mp3")
        
        # 验证结果
        mock_exists.assert_called_once_with("/tmp/input.m4a")
        mock_audio_segment.from_file.assert_called_once_with("/tmp/input.m4a")
        mock_audio.export.assert_called_once_with("/tmp/output.mp3", format="mp3")
        assert result == "/tmp/output.mp3"
