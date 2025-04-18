#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主模块测试
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from dupan_music import __version__
from dupan_music.main import main, version


class TestMain:
    """测试主模块"""

    def setup_method(self):
        """测试前准备"""
        self.runner = CliRunner()

    def test_main_help(self):
        """测试主命令帮助信息"""
        # 调用命令
        result = self.runner.invoke(main, ['--help'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "百度盘音乐命令行播放器" in result.output
        assert "auth" in result.output
        assert "api" in result.output
        assert "playlist" in result.output
        assert "player" in result.output
        assert "version" in result.output

    def test_version_command(self):
        """测试version命令"""
        # 调用命令
        result = self.runner.invoke(version)
        
        # 验证结果
        assert result.exit_code == 0
        assert "百度盘音乐命令行播放器" in result.output
        assert __version__ in result.output

    @patch('dupan_music.main.auth')
    def test_auth_command_group(self, mock_auth):
        """测试auth命令组"""
        # 设置模拟对象
        mock_auth.name = "auth"
        
        # 调用命令
        result = self.runner.invoke(main, ['auth', '--help'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "auth" in result.output

    @patch('dupan_music.main.api')
    def test_api_command_group(self, mock_api):
        """测试api命令组"""
        # 设置模拟对象
        mock_api.name = "api"
        
        # 调用命令
        result = self.runner.invoke(main, ['api', '--help'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "api" in result.output

    @patch('dupan_music.main.playlist')
    def test_playlist_command_group(self, mock_playlist):
        """测试playlist命令组"""
        # 设置模拟对象
        mock_playlist.name = "playlist"
        
        # 调用命令
        result = self.runner.invoke(main, ['playlist', '--help'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "playlist" in result.output

    @patch('dupan_music.main.player')
    def test_player_command_group(self, mock_player):
        """测试player命令组"""
        # 设置模拟对象
        mock_player.name = "player"
        
        # 调用命令
        result = self.runner.invoke(main, ['player', '--help'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "player" in result.output

    def test_version_option(self):
        """测试--version选项"""
        # 调用命令
        result = self.runner.invoke(main, ['--version'])
        
        # 验证结果
        assert result.exit_code == 0
        assert "dupan-music" in result.output
        assert __version__ in result.output
