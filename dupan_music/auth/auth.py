#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证模块
"""

import os
import json
import time
import uuid
import webbrowser
import urllib.parse
from typing import Dict, Any, Optional, Tuple
import requests
from requests.exceptions import RequestException

from dupan_music.config.config import CONFIG
from dupan_music.utils.logger import LOGGER
from dupan_music.utils.file_utils import ensure_dir, read_file, write_file


class BaiduPanAuth:
    """百度网盘认证类"""
    
    def __init__(self):
        """初始化"""
        # 获取配置
        self.app_id = CONFIG.get("app_id")
        self.app_key = CONFIG.get("app_key")
        self.secret_key = CONFIG.get("secret_key")
        self.sign_key = CONFIG.get("sign_key")
        self.redirect_uri = CONFIG.get("redirect_uri")
        self.scope = CONFIG.get("scope")
        self.oauth_url = CONFIG.get("oauth_url")
        self.api_base_url = CONFIG.get("api_base_url")
        
        # 设备信息
        self.device_id = CONFIG.get("device_id") or str(uuid.uuid4())
        self.device_name = CONFIG.get("device_name")
        
        # 如果设备ID是新生成的，则保存到配置
        if not CONFIG.get("device_id"):
            CONFIG.set("device_id", self.device_id)
            CONFIG.save()
        
        # 认证文件
        self.auth_file = CONFIG.get("storage.auth_file")
        ensure_dir(os.path.dirname(self.auth_file))
        
        # 认证信息
        self.auth_info = self._load_auth_info()
    
    def _load_auth_info(self) -> Dict[str, Any]:
        """
        加载认证信息
        
        Returns:
            Dict[str, Any]: 认证信息
        """
        # 默认认证信息
        auth_info = {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
            "scope": "",
            "session_secret": "",
            "session_key": "",
            "session_expires_at": 0,
            "user_id": "",
            "username": "",
            "is_logged_in": False,
        }
        
        # 如果认证文件存在，则加载
        if os.path.exists(self.auth_file):
            try:
                content = read_file(self.auth_file)
                if content:
                    loaded_info = json.loads(content)
                    auth_info.update(loaded_info)
            except Exception as e:
                LOGGER.error(f"加载认证文件失败: {e}")
        
        return auth_info
    
    def _save_auth_info(self) -> bool:
        """
        保存认证信息
        
        Returns:
            bool: 是否成功
        """
        if not self.auth_info["access_token"]:
            return False
        
        # 检查令牌是否过期
        if time.time() >= self.auth_info["expires_at"]:
            # 尝试刷新令牌
            if self.auth_info["refresh_token"]:
                return self.refresh_token()
            return False
        
        # 保存认证信息到文件
        try:
            write_file(self.auth_file, json.dumps(self.auth_info, ensure_ascii=False, indent=4))
            return True
        except Exception as e:
            LOGGER.error(f"保存认证信息失败: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            bool: 是否已认证
        """
        # 检查是否已登录
        if not self.auth_info.get("is_logged_in", False):
            return False
            
        # 检查是否有访问令牌
        if not self.auth_info["access_token"]:
            return False
        
        # 检查令牌是否过期
        if time.time() >= self.auth_info["expires_at"]:
            # 尝试刷新令牌
            if self.auth_info["refresh_token"]:
                return self.refresh_token()
            return False
        
        return True
    
    def get_authorize_url(self) -> str:
        """
        获取授权URL
        
        Returns:
            str: 授权URL
        """
        params = {
            "client_id": self.app_key,  # 使用app_key作为client_id
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "display": "page",
        }
        
        # 构建URL
        url_parts = []
        for key, value in params.items():
            url_parts.append(f"{key}={urllib.parse.quote(str(value))}")
        
        return f"{self.oauth_url}/authorize?{'&'.join(url_parts)}"
    
    def exchange_code_for_token(self, code: str) -> bool:
        """
        交换授权码获取令牌
        
        Args:
            code: 授权码
            
        Returns:
            bool: 是否成功
        """
        url = f"{self.oauth_url}/token"
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.app_key,  # 使用app_key作为client_id
            "client_secret": self.secret_key,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            headers = {
                "User-Agent": "pan.baidu.com"
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                LOGGER.error(f"获取令牌失败: {data}")
                return False
            
            # 更新认证信息
            self.auth_info["access_token"] = data["access_token"]
            self.auth_info["refresh_token"] = data["refresh_token"]
            self.auth_info["expires_in"] = data["expires_in"]
            self.auth_info["expires_at"] = time.time() + data["expires_in"]
            self.auth_info["scope"] = data["scope"]
            self.auth_info["is_logged_in"] = True
            
            # 保存认证信息
            return self._save_auth_info()
        except Exception as e:
            LOGGER.error(f"获取令牌失败: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """
        刷新令牌
        
        Returns:
            bool: 是否成功
        """
        if not self.auth_info["refresh_token"]:
            LOGGER.error("刷新令牌失败: 无刷新令牌")
            return False
        
        url = f"{self.oauth_url}/token"
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.auth_info["refresh_token"],
            "client_id": self.app_key,  # 使用app_key作为client_id
            "client_secret": self.secret_key,
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                LOGGER.error(f"刷新令牌失败: {data}")
                return False
            
            # 更新认证信息
            self.auth_info["access_token"] = data["access_token"]
            self.auth_info["refresh_token"] = data["refresh_token"]
            self.auth_info["expires_in"] = data["expires_in"]
            self.auth_info["expires_at"] = time.time() + data["expires_in"]
            self.auth_info["is_logged_in"] = True
            
            # 保存认证信息
            return self._save_auth_info()
        except Exception as e:
            LOGGER.error(f"刷新令牌失败: {e}")
            return False
    
    def logout(self) -> bool:
        """
        退出登录
        
        Returns:
            bool: 是否成功
        """
        if not self.auth_info["access_token"]:
            return True
        
        url = f"{self.oauth_url}/revoke"
        params = {
            "access_token": self.auth_info["access_token"],
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 清除认证信息
            self.auth_info = {
                "access_token": "",
                "refresh_token": "",
                "expires_in": 0,
                "expires_at": 0,
                "scope": "",
                "session_key": "",
                "session_secret": "",
                "is_logged_in": False,
            }
            
            # 保存认证信息
            return self._save_auth_info()
        except Exception as e:
            LOGGER.error(f"退出登录失败: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Returns:
            Optional[Dict[str, Any]]: 用户信息
        """
        if not self.is_authenticated():
            return None
        
        url = f"{self.api_base_url}/xpan/nas"
        params = {
            "method": "uinfo",
            "access_token": self.auth_info["access_token"],
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data["errno"] != 0:
                LOGGER.error(f"获取用户信息失败: {data}")
                return None
            
            return data
        except Exception as e:
            LOGGER.error(f"获取用户信息失败: {e}")
            return None
    
    def login_with_device_code(self) -> bool:
        """
        设备码模式授权登录
        
        Returns:
            bool: 是否成功
        """
        # 获取设备码和用户码
        device_code, user_code, verification_url = self._get_device_code()
        if not device_code or not user_code:
            return False
        
        # 显示用户码和验证URL
        self._display_user_code(user_code, verification_url)
        
        # 轮询设备码状态
        return self._poll_device_code_status(device_code)
    
    def _get_device_code(self) -> Tuple[str, str, str]:
        """
        获取设备码和用户码
        
        Returns:
            Tuple[str, str, str]: 设备码、用户码和验证URL
        """
        url = f"{self.oauth_url}/device/code"
        params = {
            "client_id": self.app_key,  # 使用app_key作为client_id
            "scope": self.scope,
            "response_type": "device_code",
        }
        
        try:
            headers = {
                "User-Agent": "pan.baidu.com"
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                LOGGER.error(f"获取设备码失败: {data}")
                return "", "", ""
            
            return data.get("device_code", ""), data.get("user_code", ""), data.get("verification_url", "")
        except Exception as e:
            LOGGER.error(f"获取设备码失败: {e}")
            return "", "", ""
    
    def _display_user_code(self, user_code: str, verification_url: str) -> None:
        """
        显示用户码和验证URL
        
        Args:
            user_code: 用户码
            verification_url: 验证URL
        """
        try:
            from rich.console import Console
            from rich.panel import Panel
            
            console = Console()
            console.print(Panel(f"请访问以下链接并输入用户码进行授权：\n\n验证链接: {verification_url}\n\n用户码: {user_code}", title="设备码授权", border_style="blue"))
            
            # 尝试打开浏览器
            try:
                webbrowser.open(verification_url)
                console.print("已自动打开浏览器，请在浏览器中输入用户码完成授权")
            except Exception as e:
                LOGGER.error(f"打开浏览器失败: {e}")
        except ImportError:
            print(f"请访问以下链接并输入用户码进行授权：")
            print(f"验证链接: {verification_url}")
            print(f"用户码: {user_code}")
    
    def _poll_device_code_status(self, device_code: str) -> bool:
        """
        轮询设备码状态
        
        Args:
            device_code: 设备码
            
        Returns:
            bool: 是否成功
        """
        url = f"{self.oauth_url}/token"
        params = {
            "grant_type": "device_token",
            "code": device_code,
            "client_id": self.app_key,  # 使用app_key作为client_id
            "client_secret": self.secret_key,
        }
        
        # 最多轮询60次，每次间隔5秒
        for _ in range(60):
            try:
                headers = {
                    "User-Agent": "pan.baidu.com"
                }
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # 授权成功
                if "access_token" in data:
                    # 更新认证信息
                    self.auth_info["access_token"] = data["access_token"]
                    self.auth_info["refresh_token"] = data["refresh_token"]
                    self.auth_info["expires_in"] = data["expires_in"]
                    self.auth_info["expires_at"] = time.time() + data["expires_in"]
                    self.auth_info["scope"] = data["scope"]
                    self.auth_info["is_logged_in"] = True
                    
                    # 保存认证信息
                    write_file(self.auth_file, json.dumps(self.auth_info, ensure_ascii=False, indent=4))
                    
                    return True
                
                # 授权中
                if data.get("error") == "authorization_pending":
                    print("等待用户授权中...")
                # 授权过期
                elif data.get("error") == "expired_token":
                    LOGGER.error("授权已过期")
                    return False
                # 其他错误
                else:
                    LOGGER.error(f"设备码授权失败: {data}")
                    return False
                
                time.sleep(5)
            except Exception as e:
                LOGGER.error(f"设备码授权失败: {e}")
                return False
        
        LOGGER.error("设备码授权超时")
        return False
    
    def login_with_qrcode(self) -> bool:
        """
        二维码登录（已弃用，请使用设备码模式授权）
        
        Returns:
            bool: 是否成功
        """
        LOGGER.warning("二维码登录已弃用，请使用设备码模式授权")
        return self.login_with_device_code()
