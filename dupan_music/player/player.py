#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器模块
"""

import os
import time
import tempfile
import threading
import random
from typing import Dict, List, Optional, Union, Callable, Literal
from enum import Enum
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放器模块
"""


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
        
        # 播放模式枚举
        class PlayMode(Enum):
            """播放模式枚举"""
            SEQUENTIAL = "sequential"  # 顺序播放
            LOOP = "loop"              # 循环播放
            RANDOM = "random"          # 随机播放
        
        self.PlayMode = PlayMode
        
        # 播放状态
        self.current_playlist: Optional[Playlist] = None
        self.current_item: Optional[PlaylistItem] = None
        self.current_index: int = -1
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.play_mode: PlayMode = PlayMode.LOOP  # 默认循环播放
        
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
            # 检查URL是否包含d.pcs.baidu.com域名
            is_pcs_domain = 'd.pcs.baidu.com' in download_url
            
            # 根据API文档要求，对于d.pcs.baidu.com域名必须设置User-Agent为pan.baidu.com
            if is_pcs_domain:
                # 对于d.pcs.baidu.com域名，只需要设置User-Agent为pan.baidu.com
                headers = {
                    'User-Agent': 'pan.baidu.com'
                }
                logger.debug("检测到d.pcs.baidu.com域名，设置极简请求头")
                
                # 确保URL包含access_token参数
                from urllib.parse import urlparse, parse_qs, urlunparse, parse_qsl, urlencode
                parsed_url = urlparse(download_url)
                query_params = parse_qs(parsed_url.query)
                
                if 'access_token' not in query_params and self.api.auth and self.api.auth.auth_info.get('access_token'):
                    access_token = self.api.auth.auth_info.get('access_token')
                    
                    # 重建URL，确保正确添加access_token
                    query_dict = dict(parse_qsl(parsed_url.query))
                    query_dict['access_token'] = access_token
                    
                    # 重新构建查询字符串
                    new_query = urlencode(query_dict)
                    
                    # 重新构建完整URL
                    download_url = urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    ))
                    
                    logger.debug(f"已添加access_token参数到下载链接")
                elif 'access_token' in query_params:
                    logger.debug(f"下载链接已包含access_token参数")
                else:
                    logger.warning(f"无法添加access_token参数，可能导致403错误")
            else:
                # 其他域名使用更全面的请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                    'Referer': 'https://pan.baidu.com/disk/home',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'Origin': 'https://pan.baidu.com',
                    'DNT': '1',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Range': 'bytes=0-'
                }
                
                # 添加Cookie如果有的话
                if hasattr(self.api.session, 'cookies'):
                    cookies_dict = requests.utils.dict_from_cookiejar(self.api.session.cookies)
                    if cookies_dict:
                        headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in cookies_dict.items()])
            
            logger.debug(f"开始下载文件: {item.server_filename}")
            logger.debug(f"下载链接: {download_url[:100]}...")  # 只记录链接的前100个字符
            logger.debug(f"使用请求头: {headers}")
            
            # 确保对d.pcs.baidu.com域名的请求，User-Agent始终为pan.baidu.com
            if 'd.pcs.baidu.com' in download_url and headers.get('User-Agent') != 'pan.baidu.com':
                # 根据API文档，只需要设置User-Agent为pan.baidu.com
                headers = {
                    'User-Agent': 'pan.baidu.com'
                }
                logger.debug("已设置User-Agent为pan.baidu.com并极简化请求头")
            
            # 尝试下载，最多重试3次
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 使用会话对象进行请求，这样可以保持cookie状态
                    session = requests.Session()
                    session.headers.update(headers)
                    
                    # 对于d.pcs.baidu.com域名，直接使用GET请求而不是先HEAD
                    if 'd.pcs.baidu.com' in download_url:
                        logger.debug("d.pcs.baidu.com域名，直接使用GET请求")
                        # 确保使用极简化的请求头
                        session.headers.clear()
                        session.headers.update({
                            'User-Agent': 'pan.baidu.com'
                        })
                        logger.debug(f"最终请求头: {session.headers}")
                        logger.debug(f"最终下载URL: {download_url}")
                        response = session.get(download_url, stream=True, timeout=30)
                    else:
                        # 其他域名使用原有逻辑，先发送HEAD请求
                        head_response = session.head(download_url, allow_redirects=True, timeout=10)
                        logger.debug(f"HEAD请求状态码: {head_response.status_code}")
                        if head_response.headers:
                            logger.debug(f"HEAD响应头: {head_response.headers}")
                        
                        # 如果HEAD请求成功，使用GET请求下载文件
                        if head_response.status_code == 200:
                            response = session.get(download_url, stream=True, timeout=30)
                        else:
                            # 如果HEAD请求失败但返回了重定向链接，尝试使用重定向链接
                            if head_response.status_code in (301, 302, 303, 307, 308) and 'Location' in head_response.headers:
                                redirect_url = head_response.headers['Location']
                                logger.debug(f"重定向到: {redirect_url[:100]}...")
                                # 更新Host头以匹配重定向URL
                                from urllib.parse import urlparse
                                redirect_host = urlparse(redirect_url).netloc
                                if redirect_host:
                                    headers['Host'] = redirect_host
                                response = session.get(redirect_url, stream=True, timeout=30)
                            else:
                                # 如果没有重定向，直接尝试GET请求
                                logger.debug("HEAD请求失败，尝试直接GET请求")
                                response = session.get(download_url, stream=True, timeout=30)
                    
                    response.raise_for_status()
                    
                    # 检查响应状态
                    if response.status_code == 200:
                        logger.debug(f"下载成功，开始写入临时文件")
                        break
                    else:
                        logger.warning(f"下载文件返回非200状态码: {response.status_code}，重试中...")
                        retry_count += 1
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"下载请求异常: {str(e)}")
                    if hasattr(e, 'response') and e.response:
                        logger.debug(f"错误响应状态码: {e.response.status_code}")
                        logger.debug(f"错误响应头: {e.response.headers}")
                        if e.response.content:
                            logger.debug(f"错误响应内容: {e.response.text[:500]}")  # 只记录前500个字符
                    
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"第{retry_count}次重试下载...")
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        logger.error(f"重试{max_retries}次后仍然失败")
                        return None
            
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
    
    def set_play_mode(self, mode: 'PlayMode') -> None:
        """
        设置播放模式
        
        Args:
            mode: 播放模式
        """
        self.play_mode = mode
        logger.info(f"设置播放模式: {mode.value}")
    
    def get_play_mode(self) -> str:
        """
        获取当前播放模式
        
        Returns:
            str: 播放模式名称
        """
        return self.play_mode.value
    
    def next(self) -> bool:
        """
        下一曲
        
        Returns:
            bool: 是否成功
        """
        if not self.current_playlist or not self.current_playlist.items:
            logger.warning("没有设置播放列表或播放列表为空")
            return False
        
        playlist_length = len(self.current_playlist.items)
        
        # 根据播放模式计算下一曲索引
        if self.play_mode == self.PlayMode.SEQUENTIAL:
            # 顺序播放：播放到最后一首后停止
            next_index = self.current_index + 1
            if next_index >= playlist_length:
                logger.info("已是最后一首歌曲")
                return False
                
        elif self.play_mode == self.PlayMode.LOOP:
            # 循环播放：播放到最后一首后回到第一首
            next_index = (self.current_index + 1) % playlist_length
            
        elif self.play_mode == self.PlayMode.RANDOM:
            # 随机播放：随机选择一首歌曲
            if playlist_length > 1:
                # 避免连续播放同一首歌
                next_index = random.randint(0, playlist_length - 1)
                while next_index == self.current_index and playlist_length > 1:
                    next_index = random.randint(0, playlist_length - 1)
            else:
                next_index = 0
        else:
            # 默认循环播放
            next_index = (self.current_index + 1) % playlist_length
        
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
        
        playlist_length = len(self.current_playlist.items)
        
        # 根据播放模式计算上一曲索引
        if self.play_mode == self.PlayMode.SEQUENTIAL:
            # 顺序播放：播放到第一首后停止
            prev_index = self.current_index - 1
            if prev_index < 0:
                logger.info("已是第一首歌曲")
                return False
                
        elif self.play_mode == self.PlayMode.LOOP:
            # 循环播放：播放到第一首后回到最后一首
            prev_index = (self.current_index - 1) % playlist_length
            
        elif self.play_mode == self.PlayMode.RANDOM:
            # 随机播放：随机选择一首歌曲
            if playlist_length > 1:
                # 避免连续播放同一首歌
                prev_index = random.randint(0, playlist_length - 1)
                while prev_index == self.current_index and playlist_length > 1:
                    prev_index = random.randint(0, playlist_length - 1)
            else:
                prev_index = 0
        else:
            # 默认循环播放
            prev_index = (self.current_index - 1) % playlist_length
        
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
