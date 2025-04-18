#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试播放收藏的音频文件
"""

import sys
import time
from dupan_music.auth.auth import BaiduPanAuth
from dupan_music.api.api import BaiduPanAPI
from dupan_music.player.player import AudioPlayer
from dupan_music.playlist.playlist import PlaylistManager, Playlist
from dupan_music.utils.logger import get_logger, set_log_level

# 设置日志级别为DEBUG
set_log_level("DEBUG")
logger = get_logger(__name__)

def main():
    # 初始化认证
    auth = BaiduPanAuth()
    if not auth.is_authenticated():
        logger.error("未登录，请先运行 'dupan-music auth login' 进行登录")
        return 1
    
    # 初始化API
    api = BaiduPanAPI(auth)
    
    # 初始化播放列表管理器
    playlist_manager = PlaylistManager(api)
    
    # 初始化播放器
    player = AudioPlayer(api, playlist_manager)
    
    # 获取收藏播放列表
    favorite_playlist = playlist_manager.get_favorite_playlist()
    if not favorite_playlist or not favorite_playlist.items:
        logger.error("收藏播放列表为空")
        return 1
    
    # 设置播放列表
    player.set_playlist(favorite_playlist)
    
    # 播放第一首歌
    logger.info(f"开始播放收藏的第一首歌: {favorite_playlist.items[0].server_filename}")
    player.play(0)
    
    # 等待播放完成
    try:
        while player.is_playing:
            time.sleep(1)
    except KeyboardInterrupt:
        player.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
