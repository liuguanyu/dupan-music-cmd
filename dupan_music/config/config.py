#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块
"""

import os
import json
import importlib.util
import sys
from typing import Dict, Any, Optional, List

from dupan_music.utils.file_utils import ensure_dir


class Config:
    """配置类"""
    
    def __init__(self, config_file: str = None):
        """
        初始化
        
        Args:
            config_file: 配置文件路径
        """
        # 默认配置
        self._default_config = {
            # 应用信息
            "app_name_id": "dupan-music",
            "app_name": "度盘音乐命令行",
            "app_version": "0.1.0",
            "app_description": "百度网盘音乐命令行工具",
            "app_author": "Your Name",
            "app_author_email": "your.email@example.com",
            
            # 设备信息
            "device_id": "",  # 设备ID，首次运行时生成
            "device_name": "DuPanMusic CLI",  # 设备名称
            
            # 百度网盘API
            "app_id": "",  # 百度网盘API的应用ID
            "app_key": "",  # 百度网盘API的AppKey
            "secret_key": "",  # 百度网盘API的SecretKey
            "sign_key": "",  # 百度网盘API的签名密钥
            "redirect_uri": "oob",  # 回调地址
            "scope": "basic,netdisk",  # 权限范围
            "oauth_url": "https://openapi.baidu.com/oauth/2.0",  # OAuth URL
            "api_base_url": "https://pan.baidu.com/rest/2.0",  # API基础URL
            
            # 音乐相关
            "music": {
                "default_dir": "/我的音乐",  # 默认音乐目录
                "supported_formats": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma", ".aiff", ".alac", ".ape", ".opus"],  # 支持的音乐格式
                "default_player": "",  # 默认播放器
            },
            
            # 存储相关
            "storage": {
                "base_dir": os.path.expanduser("~/.dupan-music"),  # 基础目录
                "config_file": os.path.expanduser("~/.dupan-music/config.json"),  # 配置文件
                "auth_file": os.path.expanduser("~/.dupan-music/auth.json"),  # 认证文件
                "cache_dir": os.path.expanduser("~/.dupan-music/cache"),  # 缓存目录
                "download_dir": os.path.expanduser("~/Downloads/DuPanMusic"),  # 下载目录
                "log_file": os.path.expanduser("~/.dupan-music/logs/dupan-music.log"),  # 日志文件
            },
            
            # 日志相关
            "log": {
                "level": "INFO",  # 日志级别
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
                "date_format": "%Y-%m-%d %H:%M:%S",  # 日期格式
            },
            
            # 网络相关
            "network": {
                "timeout": 30,  # 超时时间（秒）
                "retries": 3,  # 重试次数
                "chunk_size": 1024 * 1024,  # 分块大小（1MB）
            },
            
            # 界面相关
            "ui": {
                "theme": "auto",  # 主题（auto, light, dark）
                "language": "zh_CN",  # 语言
                "show_progress": True,  # 显示进度条
            },
        }
        
        # 配置文件
        self._config_file = config_file or self._default_config["storage"]["config_file"]
        
        # 确保配置目录存在
        ensure_dir(os.path.dirname(self._config_file))
        
        # 加载配置
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置
        
        Returns:
            Dict[str, Any]: 配置
        """
        # 合并默认配置
        config = self._default_config.copy()
        
        # 如果配置文件存在，则加载
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                
                # 递归合并配置
                self._merge_config(config, user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 尝试从凭据文件加载百度网盘API凭据
        try:
            # 动态导入凭据模块
            credentials_path = os.path.join(os.path.dirname(__file__), "credentials.py")
            if os.path.exists(credentials_path):
                spec = importlib.util.spec_from_file_location("credentials", credentials_path)
                credentials_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(credentials_module)
                
                if hasattr(credentials_module, "CREDENTIALS"):
                    # 更新配置中的百度网盘API凭据
                    for key, value in credentials_module.CREDENTIALS.items():
                        if key in config:
                            config[key] = value
                    print("已从凭据文件加载百度网盘API凭据")
        except Exception as e:
            print(f"加载凭据文件失败: {e}")
        
        return config
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        递归合并配置
        
        Args:
            target: 目标配置
            source: 源配置
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def save(self) -> bool:
        """
        保存配置
        
        Returns:
            bool: 是否成功
        """
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置
        
        Args:
            key: 配置键，支持点号分隔的多级键，如 "storage.base_dir"
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        # 处理多级键
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置
        
        Args:
            key: 配置键，支持点号分隔的多级键，如 "storage.base_dir"
            value: 配置值
        """
        # 处理多级键
        keys = key.split(".")
        config = self._config
        
        # 遍历到倒数第二级
        for i, k in enumerate(keys[:-1]):
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置最后一级的值
        config[keys[-1]] = value
    
    def reset(self, key: Optional[str] = None) -> None:
        """
        重置配置
        
        Args:
            key: 配置键，支持点号分隔的多级键，如 "storage.base_dir"，
                 如果为 None，则重置所有配置
        """
        if key is None:
            # 重置所有配置
            self._config = self._default_config.copy()
        else:
            # 重置指定配置
            keys = key.split(".")
            default_value = self._get_default_value(keys)
            self.set(key, default_value)
    
    def _get_default_value(self, keys: List[str]) -> Any:
        """
        获取默认值
        
        Args:
            keys: 键列表
            
        Returns:
            Any: 默认值
        """
        value = self._default_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置
        """
        return self._config.copy()
    
    def get_config_file(self) -> str:
        """
        获取配置文件路径
        
        Returns:
            str: 配置文件路径
        """
        return self._config_file


# 创建全局配置实例
CONFIG = Config()
