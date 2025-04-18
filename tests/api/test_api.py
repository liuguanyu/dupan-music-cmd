#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API模块测试
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

from dupan_music.api.api import BaiduPanAPI
from dupan_music.auth.auth import BaiduPanAuth


class TestBaiduPanAPI:
    """测试百度网盘API类"""

    def setup_method(self):
        """测试前准备"""
        # 创建模拟认证对象
        self.mock_auth = MagicMock(spec=BaiduPanAuth)
        self.mock_auth.auth_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": 9999999999,  # 未过期
            "scope": "basic,netdisk",
            "is_logged_in": True
        }
        self.mock_auth.is_authenticated.return_value = True
        
        # 创建API对象
        self.api = BaiduPanAPI(self.mock_auth)

    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """测试发送API请求（成功）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "errno": 0,
            "request_id": 123456789,
            "data": "test_data"
        }
        mock_request.return_value = mock_response
        
        # 发送请求
        result = self.api._make_request(
            method="GET",
            url="https://example.com/api",
            params={"param1": "value1"},
            data={"data1": "value1"}
        )
        
        # 验证结果
        assert result["errno"] == 0
        assert result["data"] == "test_data"
        
        # 验证请求参数
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://example.com/api"
        assert kwargs["params"]["param1"] == "value1"
        assert kwargs["params"]["access_token"] == "test_access_token"
        assert kwargs["data"] == {"data1": "value1"}

    @patch('requests.Session.request')
    def test_make_request_api_error(self, mock_request):
        """测试发送API请求（API错误）"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "errno": 111,
            "errmsg": "Access token invalid or no longer valid"
        }
        mock_request.return_value = mock_response
        
        # 发送请求
        with pytest.raises(Exception) as excinfo:
            self.api._make_request(
                method="GET",
                url="https://example.com/api"
            )
        
        # 验证异常
        assert "百度网盘API错误" in str(excinfo.value)
        assert "111" in str(excinfo.value)

    @patch('requests.Session.request')
    def test_make_request_network_error(self, mock_request):
        """测试发送API请求（网络错误）"""
        # 模拟网络错误
        mock_request.side_effect = Exception("Network error")
        
        # 发送请求
        with pytest.raises(Exception):
            self.api._make_request(
                method="GET",
                url="https://example.com/api"
            )

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_get_file_list(self, mock_make_request):
        """测试获取文件列表"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/test/file1.mp3",
                    "server_filename": "file1.mp3",
                    "size": 1024,
                    "isdir": 0
                },
                {
                    "fs_id": 789012,
                    "path": "/test/folder1",
                    "server_filename": "folder1",
                    "size": 0,
                    "isdir": 1
                }
            ]
        }
        
        # 获取文件列表
        result = self.api.get_file_list(
            dir_path="/test",
            order="name",
            desc=True,
            limit=100
        )
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["fs_id"] == 123456
        assert result[1]["fs_id"] == 789012
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["method"] == "list"
        assert kwargs["params"]["dir"] == "/test"
        assert kwargs["params"]["order"] == "name"
        assert kwargs["params"]["desc"] == 1
        assert kwargs["params"]["limit"] == 100

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_get_file_list_recursive(self, mock_make_request):
        """测试递归获取文件列表"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/test/file1.mp3",
                    "server_filename": "file1.mp3",
                    "size": 1024,
                    "isdir": 0
                },
                {
                    "fs_id": 789012,
                    "path": "/test/folder1/file2.mp3",
                    "server_filename": "file2.mp3",
                    "size": 2048,
                    "isdir": 0
                }
            ]
        }
        
        # 递归获取文件列表
        result = self.api.get_file_list_recursive(
            dir_path="/test",
            order="time",
            desc=False,
            limit=200
        )
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["fs_id"] == 123456
        assert result[1]["fs_id"] == 789012
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["method"] == "listall"
        assert kwargs["params"]["path"] == "/test"
        assert kwargs["params"]["order"] == "time"
        assert kwargs["params"]["desc"] == 0
        assert kwargs["params"]["limit"] == 200
        assert kwargs["params"]["recursion"] == 1

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_search_files(self, mock_make_request):
        """测试搜索文件"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/test/file1.mp3",
                    "server_filename": "file1.mp3",
                    "size": 1024,
                    "isdir": 0
                }
            ]
        }
        
        # 搜索文件
        result = self.api.search_files(
            key="file1",
            dir_path="/test",
            recursion=1,
            page=1,
            num=50
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0]["fs_id"] == 123456
        assert result[0]["server_filename"] == "file1.mp3"
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["method"] == "search"
        assert kwargs["params"]["key"] == "file1"
        assert kwargs["params"]["dir"] == "/test"
        assert kwargs["params"]["recursion"] == 1
        assert kwargs["params"]["page"] == 1
        assert kwargs["params"]["num"] == 50

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_get_file_info(self, mock_make_request):
        """测试获取文件信息"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "list": [
                {
                    "fs_id": 123456,
                    "path": "/test/file1.mp3",
                    "filename": "file1.mp3",
                    "size": 1024,
                    "isdir": 0,
                    "category": 2,
                    "md5": "abcdef1234567890",
                    "dlink": "https://example.com/download/file1.mp3"
                }
            ]
        }
        
        # 获取文件信息
        result = self.api.get_file_info(
            fs_ids=[123456],
            thumb=0,
            dlink=1,
            extra=1
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0]["fs_id"] == 123456
        assert result[0]["filename"] == "file1.mp3"
        assert result[0]["dlink"] == "https://example.com/download/file1.mp3"
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["method"] == "filemetas"
        assert json.loads(kwargs["params"]["fsids"]) == [123456]
        assert kwargs["params"]["thumb"] == 0
        assert kwargs["params"]["dlink"] == 1
        assert kwargs["params"]["extra"] == 1

    @patch('requests.Session.head')
    @patch('dupan_music.api.api.BaiduPanAPI.get_file_info')
    def test_get_download_link(self, mock_get_file_info, mock_head):
        """测试获取文件下载链接"""
        # 模拟文件信息
        mock_get_file_info.return_value = [
            {
                "fs_id": 123456,
                "filename": "file1.mp3",
                "dlink": "https://example.com/dlink/file1.mp3"
            }
        ]
        
        # 模拟HEAD请求响应
        mock_response = MagicMock()
        mock_response.url = "https://example.com/real_download_link/file1.mp3"
        mock_head.return_value = mock_response
        
        # 获取下载链接
        result = self.api.get_download_link(fs_id=123456)
        
        # 验证结果
        assert result == "https://example.com/real_download_link/file1.mp3"
        
        # 验证请求参数
        mock_get_file_info.assert_called_once_with([123456], dlink=1)
        mock_head.assert_called_once()
        args, kwargs = mock_head.call_args
        assert args[0] == "https://example.com/dlink/file1.mp3"
        assert kwargs["headers"]["User-Agent"] == "pan.baidu.com"
        assert kwargs["allow_redirects"] == True

    @patch('dupan_music.api.api.BaiduPanAPI.get_file_info')
    def test_get_download_link_no_file_info(self, mock_get_file_info):
        """测试获取文件下载链接（无文件信息）"""
        # 模拟无文件信息
        mock_get_file_info.return_value = []
        
        # 获取下载链接
        with pytest.raises(Exception) as excinfo:
            self.api.get_download_link(fs_id=123456)
        
        # 验证异常
        assert "无法获取文件信息" in str(excinfo.value)

    @patch('dupan_music.api.api.BaiduPanAPI.get_file_info')
    def test_get_download_link_no_dlink(self, mock_get_file_info):
        """测试获取文件下载链接（无下载链接）"""
        # 模拟无下载链接
        mock_get_file_info.return_value = [
            {
                "fs_id": 123456,
                "filename": "file1.mp3"
                # 无dlink字段
            }
        ]
        
        # 获取下载链接
        with pytest.raises(Exception) as excinfo:
            self.api.get_download_link(fs_id=123456)
        
        # 验证异常
        assert "无法获取下载链接" in str(excinfo.value)

    @patch('dupan_music.api.api.BaiduPanAPI.get_file_list')
    def test_get_audio_files(self, mock_get_file_list):
        """测试获取音频文件列表"""
        # 模拟文件列表
        mock_get_file_list.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            },
            {
                "fs_id": 234567,
                "path": "/test/file2.txt",
                "server_filename": "file2.txt",
                "size": 512,
                "isdir": 0
            },
            {
                "fs_id": 345678,
                "path": "/test/folder1",
                "server_filename": "folder1",
                "size": 0,
                "isdir": 1
            },
            {
                "fs_id": 456789,
                "path": "/test/file3.flac",
                "server_filename": "file3.flac",
                "size": 2048,
                "isdir": 0
            }
        ]
        
        # 获取音频文件列表
        result = self.api.get_audio_files(
            dir_path="/test",
            order="name",
            desc=False,
            limit=100
        )
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["fs_id"] == 123456
        assert result[0]["server_filename"] == "file1.mp3"
        assert result[1]["fs_id"] == 456789
        assert result[1]["server_filename"] == "file3.flac"
        
        # 验证请求参数
        mock_get_file_list.assert_called_once_with(
            dir_path="/test",
            order="name",
            desc=False,
            limit=100
        )

    @patch('dupan_music.api.api.BaiduPanAPI.get_file_list_recursive')
    def test_get_audio_files_recursive(self, mock_get_file_list_recursive):
        """测试递归获取音频文件列表"""
        # 模拟文件列表
        mock_get_file_list_recursive.return_value = [
            {
                "fs_id": 123456,
                "path": "/test/file1.mp3",
                "server_filename": "file1.mp3",
                "size": 1024,
                "isdir": 0
            },
            {
                "fs_id": 234567,
                "path": "/test/file2.txt",
                "server_filename": "file2.txt",
                "size": 512,
                "isdir": 0
            },
            {
                "fs_id": 345678,
                "path": "/test/folder1",
                "server_filename": "folder1",
                "size": 0,
                "isdir": 1
            },
            {
                "fs_id": 456789,
                "path": "/test/folder1/file3.wav",
                "server_filename": "file3.wav",
                "size": 2048,
                "isdir": 0
            }
        ]
        
        # 递归获取音频文件列表
        result = self.api.get_audio_files_recursive(
            dir_path="/test",
            order="time",
            desc=True,
            limit=200
        )
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["fs_id"] == 123456
        assert result[0]["server_filename"] == "file1.mp3"
        assert result[1]["fs_id"] == 456789
        assert result[1]["server_filename"] == "file3.wav"
        
        # 验证请求参数
        mock_get_file_list_recursive.assert_called_once_with(
            dir_path="/test",
            order="time",
            desc=True,
            limit=200
        )

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_get_user_info(self, mock_make_request):
        """测试获取用户信息"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "baidu_name": "test_user",
            "netdisk_name": "test_netdisk",
            "uk": 12345678,
            "vip_type": 1
        }
        
        # 获取用户信息
        result = self.api.get_user_info()
        
        # 验证结果
        assert result["errno"] == 0
        assert result["baidu_name"] == "test_user"
        assert result["netdisk_name"] == "test_netdisk"
        assert result["uk"] == 12345678
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["method"] == "uinfo"

    @patch('dupan_music.api.api.BaiduPanAPI._make_request')
    def test_get_quota(self, mock_make_request):
        """测试获取网盘容量信息"""
        # 模拟API响应
        mock_make_request.return_value = {
            "errno": 0,
            "total": 2199023255552,  # 2TB
            "used": 1099511627776,   # 1TB
            "free": 1099511627776    # 1TB
        }
        
        # 获取网盘容量信息
        result = self.api.get_quota()
        
        # 验证结果
        assert result["errno"] == 0
        assert result["total"] == 2199023255552
        assert result["used"] == 1099511627776
        assert result["free"] == 1099511627776
        
        # 验证请求参数
        mock_make_request.assert_called_once()
        args, kwargs = mock_make_request.call_args
        assert args[0] == "GET"
        assert "pan.baidu.com" in args[1]
        assert kwargs["params"]["checkfree"] == 1
        assert kwargs["params"]["checkexpire"] == 1
