#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播放列表模块
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from dupan_music.utils.logger import get_logger
from dupan_music.utils.file_utils import ensure_dir, read_file, write_file

logger = get_logger(__name__)

class PlaylistItem:
    """播放列表项"""
    
    def __init__(self, fs_id: int, server_filename: str, path: str, size: int, 
                 category: int = 0, isdir: int = 0, local_mtime: int = 0, 
                 server_mtime: int = 0, md5: str = "", add_time: int = 0):
        """
        初始化播放列表项
        
        Args:
            fs_id: 文件ID
            server_filename: 文件名
            path: 文件路径
            size: 文件大小
            category: 文件类别
            isdir: 是否是目录
            local_mtime: 本地修改时间
            server_mtime: 服务器修改时间
            md5: 文件MD5
            add_time: 添加时间
        """
        self.fs_id = fs_id
        self.server_filename = server_filename
        self.path = path
        self.size = size
        self.category = category
        self.isdir = isdir
        self.local_mtime = local_mtime
        self.server_mtime = server_mtime
        self.md5 = md5
        self.add_time = add_time or int(time.time())
    
    @classmethod
    def from_api_result(cls, api_result: Dict) -> 'PlaylistItem':
        """
        从API结果创建播放列表项
        
        Args:
            api_result: API返回的文件信息
            
        Returns:
            PlaylistItem: 播放列表项
        """
        return cls(
            fs_id=api_result.get('fs_id'),
            server_filename=api_result.get('server_filename'),
            path=api_result.get('path'),
            size=api_result.get('size'),
            category=api_result.get('category', 0),
            isdir=api_result.get('isdir', 0),
            local_mtime=api_result.get('local_mtime', 0),
            server_mtime=api_result.get('server_mtime', 0),
            md5=api_result.get('md5', ''),
            add_time=int(time.time())
        )
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            Dict: 字典表示
        """
        return {
            'fs_id': self.fs_id,
            'server_filename': self.server_filename,
            'path': self.path,
            'size': self.size,
            'category': self.category,
            'isdir': self.isdir,
            'local_mtime': self.local_mtime,
            'server_mtime': self.server_mtime,
            'md5': self.md5,
            'add_time': self.add_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlaylistItem':
        """
        从字典创建播放列表项
        
        Args:
            data: 字典数据
            
        Returns:
            PlaylistItem: 播放列表项
        """
        return cls(
            fs_id=data.get('fs_id'),
            server_filename=data.get('server_filename'),
            path=data.get('path'),
            size=data.get('size'),
            category=data.get('category', 0),
            isdir=data.get('isdir', 0),
            local_mtime=data.get('local_mtime', 0),
            server_mtime=data.get('server_mtime', 0),
            md5=data.get('md5', ''),
            add_time=data.get('add_time', int(time.time()))
        )


class Playlist:
    """播放列表"""
    
    def __init__(self, name: str, description: str = "", items: List[PlaylistItem] = None,
                 create_time: int = None, update_time: int = None):
        """
        初始化播放列表
        
        Args:
            name: 播放列表名称
            description: 播放列表描述
            items: 播放列表项
            create_time: 创建时间
            update_time: 更新时间
        """
        self.name = name
        self.description = description
        self.items = items or []
        self.create_time = create_time or int(time.time())
        self.update_time = update_time or int(time.time())
    
    def add_item(self, item: PlaylistItem) -> bool:
        """
        添加播放列表项
        
        Args:
            item: 播放列表项
            
        Returns:
            bool: 是否成功
        """
        # 检查是否已存在
        for existing_item in self.items:
            if existing_item.fs_id == item.fs_id:
                logger.debug(f"文件 {item.server_filename} 已存在于播放列表 {self.name}")
                return False
        
        self.items.append(item)
        self.update_time = int(time.time())
        return True
    
    def remove_item(self, fs_id: int) -> bool:
        """
        移除播放列表项
        
        Args:
            fs_id: 文件ID
            
        Returns:
            bool: 是否成功
        """
        original_length = len(self.items)
        self.items = [item for item in self.items if item.fs_id != fs_id]
        
        if len(self.items) < original_length:
            self.update_time = int(time.time())
            return True
        return False
    
    def clear(self) -> None:
        """清空播放列表"""
        self.items = []
        self.update_time = int(time.time())
    
    def sort_by(self, key: str, desc: bool = False) -> None:
        """
        排序播放列表
        
        Args:
            key: 排序键 ('name', 'time', 'size', 'add_time')
            desc: 是否降序
        """
        if key == 'name':
            self.items.sort(key=lambda x: x.server_filename.lower(), reverse=desc)
        elif key == 'time':
            self.items.sort(key=lambda x: x.server_mtime, reverse=desc)
        elif key == 'size':
            self.items.sort(key=lambda x: x.size, reverse=desc)
        elif key == 'add_time':
            self.items.sort(key=lambda x: x.add_time, reverse=desc)
        
        self.update_time = int(time.time())
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            Dict: 字典表示
        """
        return {
            'name': self.name,
            'description': self.description,
            'items': [item.to_dict() for item in self.items],
            'create_time': self.create_time,
            'update_time': self.update_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Playlist':
        """
        从字典创建播放列表
        
        Args:
            data: 字典数据
            
        Returns:
            Playlist: 播放列表
        """
        items = [PlaylistItem.from_dict(item) for item in data.get('items', [])]
        
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            items=items,
            create_time=data.get('create_time', int(time.time())),
            update_time=data.get('update_time', int(time.time()))
        )


class PlaylistManager:
    """播放列表管理器"""
    
    # 最近播放列表名称
    RECENT_PLAYLIST_NAME = "最近播放"
    
    # 最近播放列表最大容量
    RECENT_PLAYLIST_MAX_SIZE = 30
    
    def __init__(self, api=None):
        """
        初始化播放列表管理器
        
        Args:
            api: 百度网盘API实例
        """
        self.api = api
        self.playlists_dir = self._get_playlists_dir()
        
        # 确保目录存在
        ensure_dir(self.playlists_dir)
        
        # 确保最近播放列表存在
        self._ensure_recent_playlist()
    
    def _get_playlists_dir(self) -> str:
        """
        获取播放列表目录
        
        Returns:
            str: 播放列表目录
        """
        # 获取用户主目录
        home_dir = str(Path.home())
        
        # 播放列表目录
        playlists_dir = os.path.join(home_dir, '.dupan_music', 'playlists')
        
        return playlists_dir
    
    def _ensure_recent_playlist(self) -> None:
        """确保最近播放列表存在"""
        recent_playlist = self.get_playlist(self.RECENT_PLAYLIST_NAME)
        
        if not recent_playlist:
            # 创建最近播放列表
            recent_playlist = Playlist(
                name=self.RECENT_PLAYLIST_NAME,
                description="自动记录最近播放的音乐"
            )
            self.save_playlist(recent_playlist)
    
    def _get_playlist_path(self, name: str) -> str:
        """
        获取播放列表文件路径
        
        Args:
            name: 播放列表名称
            
        Returns:
            str: 播放列表文件路径
        """
        # 文件名安全处理
        safe_name = name.replace('/', '_').replace('\\', '_')
        
        return os.path.join(self.playlists_dir, f"{safe_name}.json")
    
    def get_all_playlists(self) -> List[Playlist]:
        """
        获取所有播放列表
        
        Returns:
            List[Playlist]: 播放列表列表
        """
        playlists = []
        
        # 遍历播放列表目录
        if os.path.exists(self.playlists_dir):
            for filename in os.listdir(self.playlists_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.playlists_dir, filename)
                    
                    try:
                        # 读取播放列表文件
                        content = read_file(file_path)
                        if content:
                            data = json.loads(content)
                            playlist = Playlist.from_dict(data)
                            playlists.append(playlist)
                    except Exception as e:
                        logger.error(f"读取播放列表文件 {file_path} 失败: {str(e)}")
        
        return playlists
    
    def get_playlist(self, name: str) -> Optional[Playlist]:
        """
        获取播放列表
        
        Args:
            name: 播放列表名称
            
        Returns:
            Optional[Playlist]: 播放列表
        """
        file_path = self._get_playlist_path(name)
        
        if os.path.exists(file_path):
            try:
                # 读取播放列表文件
                content = read_file(file_path)
                if content:
                    data = json.loads(content)
                    return Playlist.from_dict(data)
            except Exception as e:
                logger.error(f"读取播放列表 {name} 失败: {str(e)}")
        
        return None
    
    def save_playlist(self, playlist: Playlist) -> bool:
        """
        保存播放列表
        
        Args:
            playlist: 播放列表
            
        Returns:
            bool: 是否成功
        """
        file_path = self._get_playlist_path(playlist.name)
        
        try:
            # 更新时间
            playlist.update_time = int(time.time())
            
            # 转换为字典
            data = playlist.to_dict()
            
            # 写入文件
            return write_file(file_path, json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"保存播放列表 {playlist.name} 失败: {str(e)}")
            return False
    
    def create_playlist(self, name: str, description: str = "") -> Optional[Playlist]:
        """
        创建播放列表
        
        Args:
            name: 播放列表名称
            description: 播放列表描述
            
        Returns:
            Optional[Playlist]: 播放列表
        """
        # 检查是否已存在
        if self.get_playlist(name):
            logger.warning(f"播放列表 {name} 已存在")
            return None
        
        # 创建播放列表
        playlist = Playlist(name=name, description=description)
        
        # 保存播放列表
        if self.save_playlist(playlist):
            return playlist
        
        return None
    
    def delete_playlist(self, name: str) -> bool:
        """
        删除播放列表
        
        Args:
            name: 播放列表名称
            
        Returns:
            bool: 是否成功
        """
        # 不允许删除最近播放列表
        if name == self.RECENT_PLAYLIST_NAME:
            logger.warning(f"不允许删除最近播放列表")
            return False
        
        file_path = self._get_playlist_path(name)
        
        try:
            # 检查文件是否存在
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除播放列表 {name} 失败: {str(e)}")
            return False
    
    def add_to_playlist(self, playlist_name: str, file_info: Dict) -> bool:
        """
        添加文件到播放列表
        
        Args:
            playlist_name: 播放列表名称
            file_info: 文件信息
            
        Returns:
            bool: 是否成功
        """
        # 获取播放列表
        playlist = self.get_playlist(playlist_name)
        if not playlist:
            logger.warning(f"播放列表 {playlist_name} 不存在")
            return False
        
        # 创建播放列表项
        item = PlaylistItem.from_api_result(file_info)
        
        # 添加到播放列表
        if playlist.add_item(item):
            # 保存播放列表
            return self.save_playlist(playlist)
        
        return False
    
    def remove_from_playlist(self, playlist_name: str, fs_id: int) -> bool:
        """
        从播放列表移除文件
        
        Args:
            playlist_name: 播放列表名称
            fs_id: 文件ID
            
        Returns:
            bool: 是否成功
        """
        # 获取播放列表
        playlist = self.get_playlist(playlist_name)
        if not playlist:
            logger.warning(f"播放列表 {playlist_name} 不存在")
            return False
        
        # 移除文件
        if playlist.remove_item(fs_id):
            # 保存播放列表
            return self.save_playlist(playlist)
        
        return False
    
    def check_file_validity(self, fs_id: int) -> bool:
        """
        检查文件有效性
        
        Args:
            fs_id: 文件ID
            
        Returns:
            bool: 是否有效
        """
        if not self.api:
            logger.warning("未提供API实例，无法检查文件有效性")
            return False
        
        try:
            # 获取文件信息
            file_info = self.api.get_file_info([fs_id])
            
            # 如果能获取到文件信息，则文件有效
            return bool(file_info)
        except Exception as e:
            logger.error(f"检查文件有效性失败: {str(e)}")
            return False
    
    def refresh_file(self, fs_id: int) -> Optional[Dict]:
        """
        刷新文件信息
        
        Args:
            fs_id: 文件ID
            
        Returns:
            Optional[Dict]: 刷新后的文件信息
        """
        if not self.api:
            logger.warning("未提供API实例，无法刷新文件信息")
            return None
        
        try:
            # 获取文件信息
            file_info = self.api.get_file_info([fs_id])
            
            if file_info:
                return file_info[0]
            
            return None
        except Exception as e:
            logger.error(f"刷新文件信息失败: {str(e)}")
            return None
    
    def add_to_recent_playlist(self, file_info: Dict) -> bool:
        """
        添加到最近播放列表
        
        Args:
            file_info: 文件信息
            
        Returns:
            bool: 是否成功
        """
        # 获取最近播放列表
        recent_playlist = self.get_playlist(self.RECENT_PLAYLIST_NAME)
        if not recent_playlist:
            # 创建最近播放列表
            recent_playlist = self.create_playlist(
                self.RECENT_PLAYLIST_NAME,
                "自动记录最近播放的音乐"
            )
            
            if not recent_playlist:
                logger.error("创建最近播放列表失败")
                return False
        
        # 创建播放列表项
        item = PlaylistItem.from_api_result(file_info)
        
        # 移除已存在的相同文件
        recent_playlist.remove_item(item.fs_id)
        
        # 添加到列表开头
        recent_playlist.items.insert(0, item)
        
        # 限制列表大小
        if len(recent_playlist.items) > self.RECENT_PLAYLIST_MAX_SIZE:
            recent_playlist.items = recent_playlist.items[:self.RECENT_PLAYLIST_MAX_SIZE]
        
        # 更新时间
        recent_playlist.update_time = int(time.time())
        
        # 保存播放列表
        return self.save_playlist(recent_playlist)
