#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pytest配置文件
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目模块
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.api.api import BaiduPanAPI
from dupan_music.playlist.playlist import PlaylistManager
from dupan_music.player.player import AudioPlayer


@pytest.fixture
def mock_auth():
    """模拟认证对象"""
    auth = MagicMock(spec=BaiduPanAuth)
    auth.is_authenticated.return_value = True
    auth.get_access_token.return_value = "mock_access_token"
    auth.get_refresh_token.return_value = "mock_refresh_token"
    return auth


@pytest.fixture
def mock_api(mock_auth):
    """模拟API对象"""
    api = MagicMock(spec=BaiduPanAPI)
    api.auth = mock_auth
    return api


@pytest.fixture
def mock_playlist_manager(mock_api):
    """模拟播放列表管理器"""
    playlist_manager = MagicMock(spec=PlaylistManager)
    playlist_manager.api = mock_api
    return playlist_manager


@pytest.fixture
def mock_player(mock_api, mock_playlist_manager):
    """模拟播放器对象"""
    player = MagicMock(spec=AudioPlayer)
    player.api = mock_api
    player.playlist_manager = mock_playlist_manager
    return player
