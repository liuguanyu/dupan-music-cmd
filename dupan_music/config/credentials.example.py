#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证凭据模块示例 - 用于指导用户如何创建自己的凭据文件
"""

# 百度云盘 API 凭据
CREDENTIALS = {
    'app_id': '',  # 应用ID
    'app_key': '',  # 应用密钥
    'secret_key': '',  # 密钥
    'sign_key': '',  # 签名密钥
    'redirect_uri': 'oob',  # 重定向URI
    'scope': 'basic,netdisk',  # 权限范围
    'device_name': '度盘音乐',  # 设备名称
    'api_base_url': 'https://pan.baidu.com/rest/2.0',  # API基础URL
    'oauth_url': 'https://openapi.baidu.com/oauth/2.0'  # OAuth URL
}
