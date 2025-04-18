#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日志模块
"""

import os
import logging
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from dupan_music.utils.logger import get_logger, setup_logger


class TestLogger:
    """测试日志模块"""

    def test_get_logger(self):
        """测试获取日志记录器"""
        # 测试默认参数
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "dupan_music"
        
        # 测试自定义名称
        custom_logger = get_logger("custom_name")
        assert isinstance(custom_logger, logging.Logger)
        assert custom_logger.name == "custom_name"
        
        # 测试自定义日志级别
        debug_logger = get_logger(level="DEBUG")
        assert debug_logger.level == logging.DEBUG
    
    @patch("dupan_music.utils.logger.CONFIG")
    def test_setup_logger_no_file(self, mock_config):
        """测试设置日志记录器（无文件）"""
        # 模拟配置
        mock_config.get.side_effect = lambda key, default=None: {
            "log": {"level": "DEBUG", "format": "%(message)s"},
            "storage.log_file": None
        }.get(key, default)
        
        # 创建日志记录器
        logger = setup_logger("test_logger")
        
        # 验证日志级别
        assert logger.level == logging.DEBUG
        
        # 验证处理器数量（只有控制台处理器）
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    @patch("dupan_music.utils.logger.CONFIG")
    def test_setup_logger_with_file(self, mock_config):
        """测试设置日志记录器（有文件）"""
        # 创建临时日志文件
        with tempfile.NamedTemporaryFile(suffix=".log") as temp_file:
            # 模拟配置
            mock_config.get.side_effect = lambda key, default=None: {
                "log": {"level": "INFO", "format": "%(message)s"},
                "storage.log_file": temp_file.name
            }.get(key, default)
            
            # 创建日志记录器
            logger = setup_logger("test_file_logger")
            
            # 验证日志级别
            assert logger.level == logging.INFO
            
            # 验证处理器数量（控制台处理器和文件处理器）
            assert len(logger.handlers) == 2
            assert isinstance(logger.handlers[0], logging.StreamHandler)
            assert isinstance(logger.handlers[1], logging.handlers.RotatingFileHandler)
            
            # 验证文件处理器的文件名
            assert logger.handlers[1].baseFilename == temp_file.name
    
    @patch("dupan_music.utils.logger.CONFIG")
    def test_logger_functionality(self, mock_config):
        """测试日志记录器功能"""
        # 创建临时日志文件
        with tempfile.NamedTemporaryFile(suffix=".log") as temp_file:
            # 模拟配置
            mock_config.get.side_effect = lambda key, default=None: {
                "log": {"level": "DEBUG", "format": "%(message)s"},
                "storage.log_file": temp_file.name
            }.get(key, default)
            
            # 创建日志记录器
            logger = setup_logger("test_func_logger")
            
            # 记录日志
            test_message = "This is a test message"
            logger.debug(test_message)
            
            # 刷新文件处理器
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.flush()
            
            # 验证日志文件内容
            with open(temp_file.name, "r") as f:
                log_content = f.read()
                assert test_message in log_content
    
    def test_invalid_log_level(self):
        """测试无效的日志级别"""
        # 使用无效的日志级别，应该默认为INFO
        with patch("dupan_music.utils.logger.CONFIG") as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                "log": {"level": "INVALID_LEVEL"},
                "storage.log_file": None
            }.get(key, default)
            
            logger = setup_logger("test_invalid_level")
            assert logger.level == logging.INFO
