#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块测试
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock

from dupan_music.config.config import Config


class TestConfig:
    """测试配置类"""

    def setup_method(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "config.json")
        
        # 测试配置数据
        self.test_config = {
            "app_name": "测试应用",
            "app_version": "1.0.0",
            "storage": {
                "base_dir": "/tmp/test",
                "cache_dir": "/tmp/test/cache"
            },
            "ui": {
                "theme": "dark"
            }
        }
    
    def teardown_method(self):
        """测试后清理"""
        # 删除临时目录
        self.temp_dir.cleanup()
    
    def test_init_default(self):
        """测试默认初始化"""
        with patch("os.path.exists", return_value=False):
            config = Config(self.config_file)
            
            # 验证默认配置
            assert config.get("app_name") == "度盘音乐命令行"
            assert config.get("app_version") == "0.1.0"
            assert config.get("storage.base_dir") == os.path.expanduser("~/.dupan-music")
    
    def test_init_with_file(self):
        """测试从文件初始化"""
        # 模拟配置文件存在
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(self.test_config))):
            config = Config(self.config_file)
            
            # 验证配置已加载
            assert config.get("app_name") == "测试应用"
            assert config.get("app_version") == "1.0.0"
            assert config.get("storage.base_dir") == "/tmp/test"
            assert config.get("storage.cache_dir") == "/tmp/test/cache"
            assert config.get("ui.theme") == "dark"
            
            # 验证默认配置仍然存在
            assert config.get("app_description") == "百度网盘音乐命令行工具"
    
    def test_get_config(self):
        """测试获取配置"""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(self.test_config))):
            config = Config(self.config_file)
            
            # 测试获取顶级配置
            assert config.get("app_name") == "测试应用"
            
            # 测试获取嵌套配置
            assert config.get("storage.base_dir") == "/tmp/test"
            
            # 测试获取不存在的配置
            assert config.get("not_exist") is None
            assert config.get("not_exist", "默认值") == "默认值"
            
            # 测试获取不存在的嵌套配置
            assert config.get("storage.not_exist") is None
            assert config.get("not_exist.key") is None
    
    def test_set_config(self):
        """测试设置配置"""
        with patch("os.path.exists", return_value=False):
            config = Config(self.config_file)
            
            # 测试设置顶级配置
            config.set("app_name", "新应用名称")
            assert config.get("app_name") == "新应用名称"
            
            # 测试设置嵌套配置
            config.set("storage.base_dir", "/new/path")
            assert config.get("storage.base_dir") == "/new/path"
            
            # 测试设置不存在的嵌套配置
            config.set("new_section.key", "value")
            assert config.get("new_section.key") == "value"
    
    def test_reset_config(self):
        """测试重置配置"""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(self.test_config))):
            config = Config(self.config_file)
            
            # 验证初始配置
            assert config.get("app_name") == "测试应用"
            assert config.get("ui.theme") == "dark"
            
            # 重置单个配置
            config.reset("app_name")
            assert config.get("app_name") == "度盘音乐命令行"
            assert config.get("ui.theme") == "dark"  # 其他配置不变
            
            # 重置嵌套配置
            config.reset("ui.theme")
            assert config.get("ui.theme") == "auto"
            
            # 重置所有配置
            config.reset()
            assert config.get("app_name") == "度盘音乐命令行"
            assert config.get("app_version") == "0.1.0"
            assert config.get("ui.theme") == "auto"
    
    def test_save_config(self):
        """测试保存配置"""
        mock_file = mock_open()
        with patch("os.path.exists", return_value=False), \
             patch("builtins.open", mock_file):
            config = Config(self.config_file)
            
            # 修改配置
            config.set("app_name", "新应用名称")
            config.set("storage.base_dir", "/new/path")
            
            # 保存配置
            result = config.save()
            
            # 验证结果
            assert result is True
            mock_file.assert_called_once_with(self.config_file, "w", encoding="utf-8")
            
            # 验证写入的内容
            handle = mock_file()
            handle.write.assert_called_once()
            written_content = handle.write.call_args[0][0]
            saved_config = json.loads(written_content)
            assert saved_config["app_name"] == "新应用名称"
            assert saved_config["storage"]["base_dir"] == "/new/path"
    
    def test_save_config_error(self):
        """测试保存配置失败"""
        with patch("os.path.exists", return_value=False), \
             patch("builtins.open", side_effect=IOError("测试异常")), \
             patch("builtins.print") as mock_print:
            config = Config(self.config_file)
            
            # 保存配置
            result = config.save()
            
            # 验证结果
            assert result is False
            mock_print.assert_called_once_with("保存配置文件失败: 测试异常")
    
    def test_get_all_config(self):
        """测试获取所有配置"""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(self.test_config))):
            config = Config(self.config_file)
            
            # 获取所有配置
            all_config = config.get_all()
            
            # 验证结果
            assert all_config["app_name"] == "测试应用"
            assert all_config["app_version"] == "1.0.0"
            assert all_config["storage"]["base_dir"] == "/tmp/test"
            
            # 验证返回的是副本
            all_config["app_name"] = "修改后的名称"
            assert config.get("app_name") == "测试应用"  # 原配置不变
    
    def test_get_config_file(self):
        """测试获取配置文件路径"""
        with patch("os.path.exists", return_value=False):
            config = Config(self.config_file)
            
            # 获取配置文件路径
            file_path = config.get_config_file()
            
            # 验证结果
            assert file_path == self.config_file
    
    def test_load_credentials(self):
        """测试加载凭据"""
        # 模拟凭据模块
        mock_credentials = MagicMock()
        mock_credentials.CREDENTIALS = {
            "app_id": "test_app_id",
            "app_key": "test_app_key",
            "secret_key": "test_secret_key"
        }
        
        # 模拟导入凭据模块
        with patch("os.path.exists", side_effect=[False, True]), \
             patch("importlib.util.spec_from_file_location") as mock_spec, \
             patch("importlib.util.module_from_spec") as mock_module, \
             patch("builtins.print") as mock_print:
            
            # 设置模拟
            mock_spec.return_value = MagicMock()
            mock_module.return_value = mock_credentials
            
            # 初始化配置
            config = Config(self.config_file)
            
            # 验证凭据已加载
            assert config.get("app_id") == "test_app_id"
            assert config.get("app_key") == "test_app_key"
            assert config.get("secret_key") == "test_secret_key"
            
            # 验证打印信息
            mock_print.assert_called_with("已从凭据文件加载百度网盘API凭据")
    
    def test_load_credentials_error(self):
        """测试加载凭据失败"""
        with patch("os.path.exists", side_effect=[False, True]), \
             patch("importlib.util.spec_from_file_location", side_effect=ImportError("测试异常")), \
             patch("builtins.print") as mock_print:
            
            # 初始化配置
            config = Config(self.config_file)
            
            # 验证打印信息
            mock_print.assert_called_with("加载凭据文件失败: 测试异常")
