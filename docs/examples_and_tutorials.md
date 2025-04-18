# 百度盘音乐命令行播放器 示例与教程

本文档提供了百度盘音乐命令行播放器的使用示例和教程，帮助用户快速上手和了解高级功能。

## 目录

1. [基本使用](#1-基本使用)
2. [认证与登录](#2-认证与登录)
3. [文件操作](#3-文件操作)
4. [播放列表管理](#4-播放列表管理)
5. [音乐播放控制](#5-音乐播放控制)
6. [高级功能](#6-高级功能)
7. [常见问题解答](#7-常见问题解答)

## 1. 基本使用

### 1.1 安装

```bash
# 从 PyPI 安装
pip install dupan-music-cmd

# 或从源码安装
git clone https://github.com/yourusername/dupan-music-cmd.git
cd dupan-music-cmd
pip install -e .
```

### 1.2 查看帮助

```bash
# 查看主命令帮助
dupan --help

# 查看子命令帮助
dupan auth --help
dupan playlist --help
dupan player --help
```

### 1.3 命令结构

百度盘音乐命令行播放器的命令结构如下：

```
dupan [子命令组] [子命令] [参数] [选项]
```

主要子命令组包括：

- `auth`: 认证相关命令
- `api`: API相关命令
- `playlist`: 播放列表相关命令
- `player`: 播放器相关命令

## 2. 认证与登录

### 2.1 使用二维码登录

```bash
dupan auth login
```

执行后，终端会显示一个二维码，使用百度网盘 App 扫描即可登录。

### 2.2 查看登录状态

```bash
dupan auth status
```

### 2.3 退出登录

```bash
dupan auth logout
```

## 3. 文件操作

### 3.1 列出文件

```bash
# 列出根目录文件
dupan api list-files /

# 列出指定目录文件
dupan api list-files /音乐

# 按大小排序
dupan api list-files /音乐 --order size

# 降序排列
dupan api list-files /音乐 --desc
```

### 3.2 搜索文件

```bash
# 搜索包含"周杰伦"的文件
dupan api search 周杰伦

# 在指定目录中搜索
dupan api search 周杰伦 --path /音乐

# 限制返回数量
dupan api search 周杰伦 --limit 10
```

## 4. 播放列表管理

### 4.1 创建播放列表

```bash
dupan playlist create 我的最爱
```

### 4.2 列出所有播放列表

```bash
dupan playlist list-playlists
```

### 4.3 显示播放列表内容

```bash
dupan playlist show-playlist 我的最爱
```

### 4.4 添加文件到播放列表

```bash
# 添加单个文件
dupan playlist add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3

# 添加多个文件
dupan playlist add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3 /音乐/周杰伦/晴天.mp3

# 添加整个目录的音频文件
dupan playlist add-to-playlist 我的最爱 /音乐/周杰伦/
```

### 4.5 从播放列表中移除文件

```bash
# 移除索引为 0 的文件
dupan playlist remove-from-playlist 我的最爱 0

# 移除多个文件
dupan playlist remove-from-playlist 我的最爱 0 2 5
```

### 4.6 排序播放列表

```bash
# 按名称排序
dupan playlist sort-playlist 我的最爱 --key name

# 按大小降序排序
dupan playlist sort-playlist 我的最爱 --key size --reverse
```

### 4.7 导出播放列表

```bash
dupan playlist export-playlist 我的最爱 ~/我的最爱.json
```

### 4.8 导入播放列表

```bash
dupan playlist import-playlist ~/我的最爱.json
```

## 5. 音乐播放控制

### 5.1 播放音乐

```bash
# 播放指定播放列表
dupan player play 我的最爱

# 从指定索引开始播放
dupan player play 我的最爱 --index 2
```

### 5.2 暂停播放

```bash
dupan player pause
```

### 5.3 恢复播放

```bash
dupan player resume
```

### 5.4 停止播放

```bash
dupan player stop
```

### 5.5 下一曲/上一曲

```bash
dupan player next
dupan player previous
```

### 5.6 调整音量

```bash
# 查看当前音量
dupan player volume

# 设置音量为 80%
dupan player volume 80
```

### 5.7 查看播放状态

```bash
dupan player status
```

## 6. 高级功能

### 6.1 创建自动播放脚本

你可以创建一个简单的 shell 脚本来自动执行一系列命令：

```bash
#!/bin/bash
# autoplay.sh

# 登录（如果需要）
dupan auth status || dupan auth login

# 播放最近播放列表
dupan player play "最近播放"
```

使脚本可执行并运行：

```bash
chmod +x autoplay.sh
./autoplay.sh
```

### 6.2 创建定时播放任务

使用 cron 创建定时播放任务（Linux/Mac）：

```bash
# 编辑 crontab
crontab -e

# 添加以下行，每天早上 8:00 播放"早晨音乐"播放列表
0 8 * * * /path/to/dupan player play "早晨音乐"
```

### 6.3 批量添加文件

结合 shell 命令批量添加文件：

```bash
# 搜索所有周杰伦的歌曲并添加到播放列表
dupan api search 周杰伦 --limit 100 | \
  jq -r '.files[].path' | \
  xargs dupan playlist add-to-playlist "周杰伦专辑"
```

### 6.4 创建智能播放列表

通过脚本创建基于特定条件的播放列表：

```python
#!/usr/bin/env python
# smart_playlist.py

import subprocess
import json

# 搜索最近一个月添加的音乐文件
result = subprocess.check_output(
    ["dupan", "api", "search", "--json", "--time-range", "1m", "mp3"],
    text=True
)
files = json.loads(result)["files"]

# 创建新播放列表
subprocess.run(["dupan", "playlist", "create", "本月新歌"])

# 添加文件到播放列表
for file in files:
    subprocess.run(["dupan", "playlist", "add-to-playlist", "本月新歌", file["path"]])

print(f"已创建包含 {len(files)} 首歌曲的播放列表")
```

## 7. 常见问题解答

### 7.1 登录失败

**问题**：执行 `dupan auth login` 后无法成功登录。

**解决方案**：
- 确保网络连接正常
- 检查 API 密钥配置是否正确
- 尝试重新安装应用程序
- 清除缓存：`rm -rf ~/.dupan/cache`

### 7.2 播放音频失败

**问题**：无法播放某些音频文件。

**解决方案**：
- 确保已安装 ffmpeg
- 检查文件格式是否受支持
- 检查文件是否已过期，需要刷新
- 尝试使用 `dupan api list-files` 确认文件是否可访问

### 7.3 命令行显示乱码

**问题**：在某些终端中显示中文乱码。

**解决方案**：
- 确保终端支持 UTF-8 编码
- 设置环境变量：`export PYTHONIOENCODING=utf-8`
- 在 Windows 中，使用 `chcp 65001` 命令切换到 UTF-8 编码

### 7.4 播放列表文件丢失

**问题**：之前创建的播放列表找不到了。

**解决方案**：
- 播放列表文件存储在 `~/.dupan/playlists/` 目录下
- 检查该目录是否存在并有权限访问
- 如果有备份，可以使用 `dupan playlist import-playlist` 恢复

### 7.5 内存使用过高

**问题**：程序运行时内存占用过高。

**解决方案**：
- 减小播放列表大小
- 使用 `--limit` 选项限制返回结果数量
- 更新到最新版本，可能包含内存优化
- 检查是否有内存泄漏，可以提交 issue 报告

### 7.6 跨平台兼容性问题

**问题**：在不同操作系统上行为不一致。

**解决方案**：
- 确保使用最新版本
- 检查是否安装了所有依赖
- Windows 用户可能需要额外安装 VLC 媒体播放器
- 报告具体兼容性问题，帮助改进程序
