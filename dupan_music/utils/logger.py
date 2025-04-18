#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志模块
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from dupan_music.config.config import CONFIG
from dupan_music.utils.file_utils import ensure_dir

def get_logger(name: str = "dupan_music", level: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，如果为None，则使用配置中的级别
        
    Returns:
        logging.Logger: 日志记录器
    """
    return setup_logger(name, level)


def setup_logger(name: str = "dupan_music", level: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，如果为None，则使用配置中的级别
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 获取日志配置
    log_config = CONFIG.get("log", {})
    log_level = level or log_config.get("level", "INFO")
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    date_format = log_config.get("date_format", "%Y-%m-%d %H:%M:%S")
    log_file = CONFIG.get("storage.log_file")
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logger.setLevel(level_map.get(log_level.upper(), logging.INFO))
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(log_format, date_format)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，则创建文件处理器
    if log_file:
        # 确保日志目录存在
        ensure_dir(os.path.dirname(log_file))
        
        # 创建文件处理器（最大10MB，保留5个备份）
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建全局日志记录器
LOGGER = setup_logger()
