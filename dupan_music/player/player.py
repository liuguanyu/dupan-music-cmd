#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器模块
"""

import os
import time
import tempfile
import threading
from typing import Dict, List, Optional, Union, Callable

import vlc
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    import soundfile as sf
    import numpy as np
from mutagen import File as MutagenFile

from dupan_music.utils.logger import get_logger
from dupan_music.utils.file_utils import get_file_extension, get_temp_file, ensure_dir
from dupan_music.api.api import BaiduPanAPI
from dupan_music.playlist.playlist import PlaylistManager, Playlist, PlaylistItem

logger = get_logger(__name__)

class AudioPlayer:
    """音频播放器"""
    
    # 支持的音频格式
    SUPPORTED_FORMATS = ['.mp3', '.m4a', '.ogg', '.wav', '.flac', '.aiff', '.aac', '.wma']
    
    def __init__(self, api: Optional[BaiduPanAPI] = None, playlist_manager: Optional[PlaylistManager] = None):
        """
        初始化音频播放器
        
        Args:
            api: 百度网盘API实例
            playlist_manager: 播放列表管理器实例
        """
        self.api = api
        self.playlist_manager = playlist_manager
        
        # VLC实例
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.media = None
        
        # 播放状态
        self.current_playlist: Optional[Playlist] = None
        self.current_item: Optional[PlaylistItem] = None
        self.current_index: int = -1
        self.is_playing: bool = False
        self.is_paused: bool = False
        
        # 临时文件
        self.temp_file: Optional[str] = None
        
        # 事件回调
        self.on_play_callback: Optional[Callable] = None
        self.on_pause_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_next_callback: Optional[Callable] = None
        self.on_prev_callback: Optional[Callable] = None
        self.on_complete_callback: Optional[Callable] = None
        
        # 事件管理线程
        self.event_thread = None
        self.event_running = False
    
    def _start_event_thread(self) -> None:
        """启动事件管理线程"""
        if self.event_thread is not None and self.event_thread.is_alive():
            return
        
        self.event_running = True
        self.event_thread = threading.Thread(target=self._event_loop)
        self.event_thread.daemon = True
        self.event_thread.start()
    
    def _stop_event_thread(self) -> None:
        """停止事件管理线程"""
        self.event_running = False
        if self.event_thread is not None:
            self.event_thread.join(timeout=1.0)
            self.event_thread = None
    
    def _event_loop(self) -> None:
        """事件循环"""
        while self.event_running:
            # 检查播放是否结束
            if self.is_playing and not self.is_paused and self.player.get_state() == vlc.State.Ended:
                self.is_playing = False
                logger.debug("播放结束")
                
                # 调用完成回调
                if self.on_complete_callback:
                    self.on_complete_callback()
                
                # 自动播放下一曲
                self.next()
            
            time.sleep(0.5)
    
    def _clean_temp_file(self) -> None:
        """清理临时文件"""
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
                self.temp_file = None
            except Exception as e:
                logger.error(f"清理临时文件失败: {str(e)}")
    
    def _download_file(self, item: PlaylistItem) -> Optional[str]:
        """
        下载文件
        
        Args:
            item: 播放列表项
            
        Returns:
            Optional[str]: 临时文件路径
        """
        if not self.api:
            logger.error("未提供API实例，无法下载文件")
            return None
        
        try:
            # 获取下载链接
            download_url = self.api.get_download_link(item.fs_id)
            
            # 创建临时文件
            ext = get_file_extension(item.server_filename)
            temp_file = get_temp_file(suffix=ext)
            
            # 下载文件
            import requests
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_file
        except Exception as e:
            logger.error(f"下载文件失败: {str(e)}")
            return None
    
    def _check_file_validity(self, item: PlaylistItem) -> bool:
        """
        检查文件有效性
        
        Args:
            item: 播放列表项
            
        Returns:
            bool: 是否有效
        """
        if not self.playlist_manager:
            logger.warning("未提供播放列表管理器，无法检查文件有效性")
            return True
        
        return self.playlist_manager.check_file_validity(item.fs_id)
    
    def _refresh_file(self, item: PlaylistItem) -> Optional[PlaylistItem]:
        """
        刷新文件信息
        
        Args:
            item: 播放列表项
            
        Returns:
            Optional[PlaylistItem]: 刷新后的播放列表项
        """
        if not self.playlist_manager:
            logger.warning("未提供播放列表管理器，无法刷新文件信息")
            return None
        
        file_info = self.playlist_manager.refresh_file(item.fs_id)
        if file_info:
            return PlaylistItem.from_api_result(file_info)
        
        return None
    
    def set_playlist(self, playlist: Playlist) -> bool:
        """
        设置播放列表
        
        Args:
            playlist: 播放列表
            
        Returns:
            bool: 是否成功
        """
        # 停止当前播放
        self.stop()
        
        # 设置播放列表
        self.current_playlist = playlist
        self.current_item = None
        self.current_index = -1
        
        return True
    
    def play(self, index: int = 0) -> bool:
        """
        播放
        
        Args:
            index: 播放索引
            
        Returns:
            bool: 是否成功
        """
        if not self.current_playlist or not self.current_playlist.items:
            logger.warning("没有设置播放列表或播放列表为空")
            return False
        
        # 检查索引是否有效
        if index < 0 or index >= len(self.current_playlist.items):
            logger.warning(f"无效的播放索引: {index}")
            return False
        
        # 停止当前播放
        self.stop()
        
        # 设置当前项
        self.current_index = index
        self.current_item = self.current_playlist.items[index]
        
        # 检查文件有效性
        if not self._check_file_validity(self.current_item):
            logger.warning(f"文件无效: {self.current_item.server_filename}")
            
            # 尝试刷新文件信息
            refreshed_item = self._refresh_file(self.current_item)
            if not refreshed_item:
                logger.error(f"刷新文件信息失败: {self.current_item.server_filename}")
                return False
            
            # 更新当前项
            self.current_item = refreshed_item
            self.current_playlist.items[index] = refreshed_item
        
        # 下载文件
        self.temp_file = self._download_file(self.current_item)
        if not self.temp_file:
            logger.error(f"下载文件失败: {self.current_item.server_filename}")
            return False
        
        try:
            # 创建媒体
            self.media = self.instance.media_new(self.temp_file)
            self.player.set_media(self.media)
            
            # 播放
            result = self.player.play()
            if result == 0:
                self.is_playing = True
                self.is_paused = False
                
                # 添加到最近播放列表
                if self.playlist_manager:
                    self.playlist_manager.add_to_recent_playlist(self.current_item.to_dict())
                
                # 启动事件线程
                self._start_event_thread()
                
                # 调用播放回调
                if self.on_play_callback:
                    self.on_play_callback(self.current_item)
                
                logger.info(f"正在播放: {self.current_item.server_filename}")
                return True
            else:
                logger.error(f"播放失败: {result}")
                return False
        except Exception as e:
            logger.error(f"播放异常: {str(e)}")
            return False
    
    def pause(self) -> bool:
        """
        暂停/恢复
        
        Returns:
            bool: 是否成功
        """
        if not self.is_playing:
            logger.warning("当前没有播放")
            return False
        
        if self.is_paused:
            # 恢复播放
            self.player.play()
            self.is_paused = False
            logger.info("恢复播放")
            
            # 调用播放回调
            if self.on_play_callback:
                self.on_play_callback(self.current_item)
        else:
            # 暂停播放
            self.player.pause()
            self.is_paused = True
            logger.info("暂停播放")
            
            # 调用暂停回调
            if self.on_pause_callback:
                self.on_pause_callback()
        
        return True
    
    def stop(self) -> bool:
        """
        停止
        
        Returns:
            bool: 是否成功
        """
        if not self.is_playing:
            return True
        
        # 停止播放
        self.player.stop()
        self.is_playing = False
        self.is_paused = False
        
        # 清理临时文件
        self._clean_temp_file()
        
        # 调用停止回调
        if self.on_stop_callback:
            self.on_stop_callback()
        
        logger.info("停止播放")
        return True
    
    def next(self) -> bool:
        """
        下一曲
        
        Returns:
            bool: 是否成功
        """
        if not self.current_playlist or not self.current_playlist.items:
            logger.warning("没有设置播放列表或播放列表为空")
            return False
        
        # 计算下一曲索引
        next_index = self.current_index + 1
        if next_index >= len(self.current_playlist.items):
            next_index = 0  # 循环播放
        
        # 播放下一曲
        result = self.play(next_index)
        
        # 调用下一曲回调
        if result and self.on_next_callback:
            self.on_next_callback(self.current_item)
        
        return result
    
    def prev(self) -> bool:
        """
        上一曲
        
        Returns:
            bool: 是否成功
        """
        if not self.current_playlist or not self.current_playlist.items:
            logger.warning("没有设置播放列表或播放列表为空")
            return False
        
        # 计算上一曲索引
        prev_index = self.current_index - 1
        if prev_index < 0:
            prev_index = len(self.current_playlist.items) - 1  # 循环播放
        
        # 播放上一曲
        result = self.play(prev_index)
        
        # 调用上一曲回调
        if result and self.on_prev_callback:
            self.on_prev_callback(self.current_item)
        
        return result
    
    def set_volume(self, volume: int) -> bool:
        """
        设置音量
        
        Args:
            volume: 音量 (0-100)
            
        Returns:
            bool: 是否成功
        """
        # 限制音量范围
        volume = max(0, min(100, volume))
        
        # 设置音量
        self.player.audio_set_volume(volume)
        logger.info(f"设置音量: {volume}")
        return True
    
    def get_volume(self) -> int:
        """
        获取音量
        
        Returns:
            int: 音量 (0-100)
        """
        return self.player.audio_get_volume()
    
    def get_position(self) -> float:
        """
        获取播放位置
        
        Returns:
            float: 播放位置 (0.0-1.0)
        """
        if not self.is_playing:
            return 0.0
        
        return self.player.get_position()
    
    def set_position(self, position: float) -> bool:
        """
        设置播放位置
        
        Args:
            position: 播放位置 (0.0-1.0)
            
        Returns:
            bool: 是否成功
        """
        if not self.is_playing:
            logger.warning("当前没有播放")
            return False
        
        # 限制位置范围
        position = max(0.0, min(1.0, position))
        
        # 设置位置
        self.player.set_position(position)
        logger.info(f"设置播放位置: {position:.2f}")
        return True
    
    def get_time(self) -> int:
        """
        获取播放时间
        
        Returns:
            int: 播放时间（毫秒）
        """
        if not self.is_playing:
            return 0
        
        return self.player.get_time()
    
    def get_length(self) -> int:
        """
        获取音频长度
        
        Returns:
            int: 音频长度（毫秒）
        """
        if not self.is_playing or not self.media:
            return 0
        
        return self.media.get_duration()
    
    def get_metadata(self) -> Dict:
        """
        获取音频元数据
        
        Returns:
            Dict: 元数据
        """
        if not self.temp_file or not os.path.exists(self.temp_file):
            return {}
        
        try:
            # 使用mutagen获取元数据
            audio_file = MutagenFile(self.temp_file)
            if not audio_file:
                return {}
            
            metadata = {}
            
            # 提取常见标签
            for key, value in audio_file.items():
                if isinstance(value, list) and value:
                    metadata[key] = value[0]
                else:
                    metadata[key] = value
            
            return metadata
        except Exception as e:
            logger.error(f"获取元数据失败: {str(e)}")
            return {}
    
    def convert_format(self, input_file: str, output_format: str = "mp3") -> Optional[str]:
        """
        转换音频格式
        
        Args:
            input_file: 输入文件路径
            output_format: 输出格式
            
        Returns:
            Optional[str]: 输出文件路径
        """
        if not os.path.exists(input_file):
            logger.error(f"输入文件不存在: {input_file}")
            return None
        
        # 检查输出格式是否支持
        output_ext = f".{output_format.lower()}"
        if output_ext not in self.SUPPORTED_FORMATS:
            logger.error(f"不支持的输出格式: {output_format}")
            return None
        
        try:
            # 创建输出文件
            output_file = get_temp_file(suffix=output_ext)
            
            if PYDUB_AVAILABLE:
                # 使用pydub加载音频
                audio = AudioSegment.from_file(input_file)
                # 导出为指定格式
                audio.export(output_file, format=output_format)
            else:
                # 使用soundfile加载音频
                data, samplerate = sf.read(input_file)
                # 导出为指定格式
                sf.write(output_file, data, samplerate, format=output_format.upper())
            
            return output_file
        except Exception as e:
            logger.error(f"转换格式失败: {str(e)}")
            return None
    
    def __del__(self):
        """析构函数"""
        # 停止播放
        self.stop()
        
        # 停止事件线程
        self._stop_event_thread()
