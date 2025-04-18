#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API封装模块
"""

import os
import json
import time
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
        # 直接使用filemetas接口获取下载链接
        url = f"{self.PAN_API_URL}/multimedia"
        params = {
            'method': 'filemetas',
            'fsids': json.dumps([fs_id]),
            'dlink': 1,  # 请求下载链接
            'access_token': self.auth.auth_info["access_token"]
        }
        
        # 发送请求
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
            'Pragma': 'no-cache'
        }
        
        try:
            # 最多重试3次
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = self.session.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    
                    # 检查API错误
                    if 'errno' in result and result['errno'] != 0:
                        error_msg = f"百度网盘API错误: {result.get('errmsg', '未知错误')} (错误码: {result['errno']})"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    # 获取下载链接
                    if not result.get('list') or len(result['list']) == 0:
                        raise Exception(f"无法获取文件信息: {fs_id}")
                    
                    dlink = result['list'][0].get('dlink')
                    if not dlink:
                        raise Exception(f"无法获取下载链接: {fs_id}")
                    
                    # 使用HEAD请求获取真实下载链接（处理重定向）
                    try:
                        logger.debug(f"获取到的初始下载链接: {dlink[:100]}...")  # 只记录链接的前100个字符
                        
                        # 创建新的会话对象，确保请求头正确应用
                        session = requests.Session()
                        
                        # 检查是否是d.pcs.baidu.com域名
                        is_pcs_domain = 'd.pcs.baidu.com' in dlink
                        
                        # 根据API文档要求，对于d.pcs.baidu.com域名必须设置User-Agent为pan.baidu.com
                        if is_pcs_domain:
                            # 对于d.pcs.baidu.com域名，只需要设置User-Agent为pan.baidu.com
                            request_headers = {
                                'User-Agent': 'pan.baidu.com'
                            }
                            logger.debug("检测到d.pcs.baidu.com域名，设置极简请求头")
                            
                            # 确保URL包含access_token参数
                            from urllib.parse import urlparse, parse_qs, urlunparse, parse_qsl, urlencode
                            parsed_url = urlparse(dlink)
                            query_params = parse_qs(parsed_url.query)
                            
                            if 'access_token' not in query_params and self.auth.auth_info.get('access_token'):
                                access_token = self.auth.auth_info.get('access_token')
                                
                                # 重建URL，确保正确添加access_token
                                query_dict = dict(parse_qsl(parsed_url.query))
                                query_dict['access_token'] = access_token
                                
                                # 重新构建查询字符串
                                new_query = urlencode(query_dict)
                                
                                # 重新构建完整URL
                                dlink = urlunparse((
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
                            request_headers = {
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
                            if hasattr(self.session, 'cookies'):
                                cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
                                if cookies_dict:
                                    request_headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in cookies_dict.items()])
                        
                        session.headers.update(request_headers)
                        
                        # 对于d.pcs.baidu.com域名，直接返回处理后的链接，不需要HEAD请求
                        if is_pcs_domain:
                            logger.debug(f"d.pcs.baidu.com域名，直接返回处理后的链接")
                            # 确保使用极简化的请求头
                            session.headers.clear()
                            session.headers.update({
                                'User-Agent': 'pan.baidu.com'
                            })
                            logger.debug(f"最终请求头: {session.headers}")
                            logger.debug(f"最终下载URL: {dlink}")
                            return dlink
                        
                        # 其他域名使用HEAD请求获取真实链接
                        head_response = session.head(dlink, allow_redirects=True, timeout=10)
                        
                        # 如果HEAD请求成功并有重定向
                        if head_response.history:
                            real_url = head_response.url
                            logger.debug(f"重定向到真实下载链接: {real_url[:100]}...")
                            return real_url
                        
                        # 如果HEAD请求成功但没有重定向
                        if head_response.status_code == 200:
                            return dlink
                        # 如果HEAD请求失败但返回了重定向链接
                        elif head_response.status_code in (301, 302, 303, 307, 308) and 'Location' in head_response.headers:
                            final_url = head_response.headers['Location']
                            logger.debug(f"重定向到真实下载链接: {final_url[:100]}...")
                            return final_url
                        else:
                            return dlink
                    except Exception as e:
                        logger.warning(f"获取真实下载链接失败，将使用原始链接: {str(e)}")
                    
                    # 如果获取重定向失败，返回原始链接
                    return dlink
                    
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"请求错误，第{retry_count}次重试: {str(e)}")
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        logger.error(f"请求错误，重试{max_retries}次后仍然失败: {str(e)}")
                        raise
            
            # 如果所有重试都失败，抛出异常
            raise Exception(f"获取下载链接失败，重试{max_retries}次后仍然失败")
            
        except Exception as e:
            logger.error(f"获取下载链接失败: {str(e)}")
            raise
    
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
