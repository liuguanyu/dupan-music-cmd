#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API封装模块
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode

from dupan_music.utils.logger import get_logger
from dupan_music.auth.auth import BaiduPanAuth

logger = get_logger(__name__)

class BaiduPanAPI:
    """百度网盘API封装类"""
    
    # API基础URL
    PAN_API_URL = "https://pan.baidu.com/rest/2.0/xpan"
    
    def __init__(self, auth: BaiduPanAuth):
        """
        初始化百度网盘API
        
        Args:
            auth: 百度网盘认证对象
        """
        self.auth = auth
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
        })
    
    def _make_request(self, method: str, url: str, params: Dict = None, data: Dict = None, 
                     files: Dict = None, json_data: Dict = None, **kwargs) -> Dict:
        """
        发送API请求
        
        Args:
            method: 请求方法 (GET, POST, etc.)
            url: 请求URL
            params: URL参数
            data: 表单数据
            files: 文件数据
            json_data: JSON数据
            **kwargs: 其他参数
            
        Returns:
            API响应数据
        """
        # 确保有访问令牌
        if not self.auth.is_authenticated():
            self.auth.refresh_token()
        
        # 添加访问令牌到参数
        if params is None:
            params = {}
        params['access_token'] = self.auth.auth_info["access_token"]
        
        # 发送请求
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                json=json_data,
                **kwargs
            )
            response.raise_for_status()
            result = response.json()
            
            # 检查API错误
            if 'errno' in result and result['errno'] != 0:
                error_msg = f"百度网盘API错误: {result.get('errmsg', '未知错误')} (错误码: {result['errno']})"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"请求错误: {str(e)}")
            raise
    
    def get_file_list(self, dir_path: str = '/', order: str = 'name', 
                     desc: bool = False, limit: int = 1000, 
                     web: str = 'web', folder: int = 0) -> List[Dict]:
        """
        获取文件列表
        
        Args:
            dir_path: 目录路径
            order: 排序方式 ('name', 'time', 'size')
            desc: 是否降序排序
            limit: 返回条目数量限制
            web: 请求来源
            folder: 是否只返回文件夹 (0: 全部, 1: 只返回文件夹)
            
        Returns:
            文件列表
        """
        url = f"{self.PAN_API_URL}/file"
        params = {
            'method': 'list',
            'dir': dir_path,
            'order': order,
            'desc': 1 if desc else 0,
            'limit': limit,
            'web': web,
            'folder': folder
        }
        
        result = self._make_request('GET', url, params=params)
        return result.get('list', [])
    
    def get_file_list_recursive(self, dir_path: str = '/', order: str = 'name',
                              desc: bool = False, limit: int = 1000,
                              web: str = 'web', folder: int = 0,
                              start: int = 0, recursion: int = 1) -> List[Dict]:
        """
        递归获取文件列表
        
        Args:
            dir_path: 目录路径
            order: 排序方式 ('name', 'time', 'size')
            desc: 是否降序排序
            limit: 返回条目数量限制
            web: 请求来源
            folder: 是否只返回文件夹 (0: 全部, 1: 只返回文件夹)
            start: 起始位置
            recursion: 是否递归获取子目录 (0: 不递归, 1: 递归)
            
        Returns:
            文件列表
        """
        url = f"{self.PAN_API_URL}/multimedia"
        params = {
            'method': 'listall',
            'path': dir_path,
            'order': order,
            'desc': 1 if desc else 0,
            'limit': limit,
            'web': web,
            'folder': folder,
            'start': start,
            'recursion': recursion
        }
        
        result = self._make_request('GET', url, params=params)
        return result.get('list', [])
    
    def search_files(self, key: str, dir_path: str = '/', 
                    recursion: int = 1, page: int = 1, 
                    num: int = 100, web: str = 'web') -> List[Dict]:
        """
        搜索文件
        
        Args:
            key: 搜索关键词
            dir_path: 搜索目录
            recursion: 是否递归搜索子目录 (0: 不递归, 1: 递归)
            page: 页码
            num: 每页数量
            web: 请求来源
            
        Returns:
            搜索结果列表
        """
        url = f"{self.PAN_API_URL}/file"
        params = {
            'method': 'search',
            'key': key,
            'dir': dir_path,
            'recursion': recursion,
            'page': page,
            'num': num,
            'web': web
        }
        
        result = self._make_request('GET', url, params=params)
        return result.get('list', [])
    
    def get_file_info(self, fs_ids: List[int], thumb: int = 0, 
                     dlink: int = 0, extra: int = 0) -> List[Dict]:
        """
        获取文件信息
        
        Args:
            fs_ids: 文件ID列表
            thumb: 是否获取缩略图 (0: 不获取, 1: 获取)
            dlink: 是否获取下载链接 (0: 不获取, 1: 获取)
            extra: 是否获取额外信息 (0: 不获取, 1: 获取)
            
        Returns:
            文件信息列表
        """
        url = f"{self.PAN_API_URL}/multimedia"
        params = {
            'method': 'filemetas',
            'fsids': json.dumps(fs_ids),
            'thumb': thumb,
            'dlink': dlink,
            'extra': extra
        }
        
        result = self._make_request('GET', url, params=params)
        return result.get('list', [])
    
    def get_download_link(self, fs_id: int) -> str:
        """
        获取文件下载链接
        
        Args:
            fs_id: 文件ID
            
        Returns:
            下载链接
        """
        file_info = self.get_file_info([fs_id], dlink=1)
        if not file_info:
            raise Exception(f"无法获取文件信息: {fs_id}")
        
        dlink = file_info[0].get('dlink')
        if not dlink:
            raise Exception(f"无法获取下载链接: {fs_id}")
        
        # 获取真实下载链接
        response = self.session.head(
            dlink,
            headers={'User-Agent': 'pan.baidu.com'},
            allow_redirects=True
        )
        
        return response.url
    
    def get_audio_files(self, dir_path: str = '/', order: str = 'name', 
                       desc: bool = False, limit: int = 1000) -> List[Dict]:
        """
        获取音频文件列表（非递归）
        
        Args:
            dir_path: 目录路径
            order: 排序方式 ('name', 'time', 'size')
            desc: 是否降序排序
            limit: 返回条目数量限制
            
        Returns:
            音频文件列表
        """
        # 支持的音频文件扩展名
        audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']
        
        # 获取文件列表（非递归）
        files = self.get_file_list(dir_path, order, desc, limit)
        
        # 过滤音频文件
        audio_files = [
            file for file in files 
            if file.get('isdir') == 0 and 
            os.path.splitext(file.get('server_filename', ''))[1].lower() in audio_extensions
        ]
        
        return audio_files
    
    def get_audio_files_recursive(self, dir_path: str = '/', order: str = 'name', 
                                desc: bool = False, limit: int = 1000) -> List[Dict]:
        """
        递归获取音频文件列表
        
        Args:
            dir_path: 目录路径
            order: 排序方式 ('name', 'time', 'size')
            desc: 是否降序排序
            limit: 返回条目数量限制
            
        Returns:
            音频文件列表
        """
        # 支持的音频文件扩展名
        audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac', '.wma']
        
        # 获取文件列表（递归）
        files = self.get_file_list_recursive(dir_path, order, desc, limit)
        
        # 过滤音频文件
        audio_files = [
            file for file in files 
            if file.get('isdir') == 0 and 
            os.path.splitext(file.get('server_filename', ''))[1].lower() in audio_extensions
        ]
        
        return audio_files
    
    def get_user_info(self) -> Dict:
        """
        获取用户信息
        
        Returns:
            用户信息
        """
        url = "https://pan.baidu.com/rest/2.0/xpan/nas"
        params = {
            'method': 'uinfo'
        }
        
        return self._make_request('GET', url, params=params)
    
    def get_quota(self) -> Dict:
        """
        获取网盘容量信息
        
        Returns:
            容量信息
        """
        url = "https://pan.baidu.com/api/quota"
        params = {
            'checkfree': 1,
            'checkexpire': 1
        }
        
        return self._make_request('GET', url, params=params)
