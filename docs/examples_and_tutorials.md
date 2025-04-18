# 百度盘音乐命令行播放器 示例与教程

本文档提供了百度盘音乐命令行播放器的使用示例和教程，帮助用户快速上手和了解高级功能。

## 目录

1. [基本使用](#1-基本使用)
2. [认证与登录](#2-认证与登录)
3. [文件操作](#3-文件操作)
4. [播放列表管理](#4-播放列表管理)
5. [音乐播放控制](#5-音乐播放控制)
6. [交互式Shell](#6-交互式shell)
7. [高级功能](#7-高级功能)
8. [常见问题解答](#8-常见问题解答)

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
dupan-music --help

# 查看子命令帮助
dupan-music auth --help
dupan-music playlist --help
dupan-music player --help
```

### 1.3 命令结构

百度盘音乐命令行播放器的命令结构如下：

```
dupan-music [子命令组] [子命令] [参数] [选项]
```

主要子命令组包括：

- `auth`: 认证相关命令
- `api`: API相关命令
- `playlist`: 播放列表相关命令
- `player`: 播放器相关命令

## 2. 认证与登录

### 2.1 使用二维码登录

```bash
dupan-music auth login
```

执行后，终端会显示一个二维码，使用百度网盘 App 扫描即可登录。

### 2.2 查看登录状态

```bash
dupan-music auth status
```

### 2.3 退出登录

```bash
dupan-music auth logout
```

## 3. 文件操作

### 3.1 列出文件

```bash
# 列出根目录文件
dupan-music api list-files /

# 列出指定目录文件
dupan-music api list-files /音乐

# 按大小排序
dupan-music api list-files /音乐 --order size

# 降序排列
dupan-music api list-files /音乐 --desc
```

### 3.2 搜索文件

```bash
# 搜索包含"周杰伦"的文件
dupan-music api search 周杰伦

# 在指定目录中搜索
dupan-music api search 周杰伦 --path /音乐

# 限制返回数量
dupan-music api search 周杰伦 --limit 10
```

## 4. 播放列表管理

### 4.1 创建播放列表

```bash
dupan-music playlist create 我的最爱
```

### 4.2 列出所有播放列表

```bash
dupan-music playlist list-playlists
```

### 4.3 显示播放列表内容

```bash
dupan-music playlist show-playlist 我的最爱
```

### 4.4 添加文件到播放列表

```bash
# 添加单个文件
dupan-music playlist add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3

# 添加多个文件
dupan-music playlist add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3 /音乐/周杰伦/晴天.mp3

# 添加整个目录的音频文件
dupan-music playlist add-to-playlist 我的最爱 /音乐/周杰伦/
```

### 4.5 从播放列表中移除文件

```bash
# 移除索引为 0 的文件
dupan-music playlist remove-from-playlist 我的最爱 0

# 移除多个文件
dupan-music playlist remove-from-playlist 我的最爱 0 2 5
```

### 4.6 排序播放列表

```bash
# 按名称排序
dupan-music playlist sort-playlist 我的最爱 --key name

# 按大小降序排序
dupan-music playlist sort-playlist 我的最爱 --key size --reverse
```

### 4.7 导出播放列表

```bash
dupan-music playlist export-playlist 我的最爱 ~/我的最爱.json
```

### 4.8 导入播放列表

```bash
dupan-music playlist import-playlist ~/我的最爱.json
```

## 5. 音乐播放控制

### 5.1 播放音乐

```bash
# 播放指定播放列表
dupan-music player play 我的最爱

# 从指定索引开始播放
dupan-music player play 我的最爱 --index 2
```

### 5.2 暂停播放

```bash
dupan-music player pause
```

### 5.3 恢复播放

```bash
dupan-music player resume
```

### 5.4 停止播放

```bash
dupan-music player stop
```

### 5.5 下一曲/上一曲

```bash
dupan-music player next
dupan-music player previous
```

### 5.6 调整音量

```bash
# 查看当前音量
dupan-music player volume

# 设置音量为 80%
dupan-music player volume 80
```

### 5.7 查看播放状态

```bash
dupan-music player status
```

## 6. 交互式Shell

### 6.1 启动交互式Shell

```bash
# 启动交互式Shell
dupan-music shell

# 使用特定配置文件启动
dupan-music shell --config ~/.dupan/custom_config.json
```

### 6.2 交互式Shell命令

在交互式Shell中，你可以使用以下命令：

```
# 查看可用命令
help

# 查看特定命令的帮助
help play

# 认证命令
login
logout
status

# 文件操作
list-files /音乐
search 周杰伦

# 播放列表管理
create-playlist 我的最爱
list-playlists
show-playlist 我的最爱
add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3
remove-from-playlist 我的最爱 0

# 播放控制
play 我的最爱
pause
resume
stop
next
previous
volume 80
status

# 退出Shell
exit
quit
```

### 6.3 Shell功能特点

- **命令自动补全**：按Tab键可以自动补全命令和参数
- **历史记录**：使用上下箭头键可以浏览命令历史
- **彩色输出**：不同类型的信息使用不同颜色显示
- **实时状态更新**：播放状态实时显示在提示符中

### 6.4 Shell配置

交互式Shell的配置存储在`~/.dupan/shell_config.json`文件中，可以自定义以下设置：

```json
{
  "prompt": "\u001b[32mdupan>\u001b[0m ",
  "history_file": "~/.dupan/shell_history",
  "max_history": 1000,
  "auto_complete": true,
  "color_scheme": {
    "command": "green",
    "error": "red",
    "info": "blue",
    "success": "green"
  }
}
```

## 7. 高级功能

### 7.1 创建自动播放脚本

你可以创建一个简单的 shell 脚本来自动执行一系列命令：

```bash
#!/bin/bash
# autoplay.sh

# 登录（如果需要）
dupan-music auth status || dupan-music auth login

# 播放最近播放列表
dupan-music player play "最近播放"
```

使脚本可执行并运行：

```bash
chmod +x autoplay.sh
./autoplay.sh
```

### 7.2 创建定时播放任务

使用 cron 创建定时播放任务（Linux/Mac）：

```bash
# 编辑 crontab
crontab -e

# 添加以下行，每天早上 8:00 播放"早晨音乐"播放列表
0 8 * * * /path/to/dupan-music player play "早晨音乐"
```

### 7.3 批量添加文件

结合 shell 命令批量添加文件：

```bash
# 搜索所有周杰伦的歌曲并添加到播放列表
dupan-music api search 周杰伦 --limit 100 | \
  jq -r '.files[].path' | \
  xargs dupan-music playlist add-to-playlist "周杰伦专辑"
```

### 7.4 创建智能播放列表

通过脚本创建基于特定条件的播放列表：

```python
#!/usr/bin/env python
# smart_playlist.py

import subprocess
import json

# 搜索最近一个月添加的音乐文件
result = subprocess.check_output(
    ["dupan-music", "api", "search", "--json", "--time-range", "1m", "mp3"],
    text=True
)
files = json.loads(result)["files"]

# 创建新播放列表
subprocess.run(["dupan-music", "playlist", "create", "本月新歌"])

# 添加文件到播放列表
for file in files:
    subprocess.run(["dupan-music", "playlist", "add-to-playlist", "本月新歌", file["path"]])

print(f"已创建包含 {len(files)} 首歌曲的播放列表")
```

## 8. 常见问题解答

### 8.1 登录失败

**问题**：执行 `dupan-music auth login` 后无法成功登录。

**解决方案**：
- 确保网络连接正常
- 检查 API 密钥配置是否正确
- 尝试重新安装应用程序
- 清除缓存：`rm -rf ~/.dupan/cache`

### 8.2 播放音频失败

**问题**：无法播放某些音频文件。

**解决方案**：
- 确保已安装 ffmpeg
- 检查文件格式是否受支持
- 检查文件是否已过期，需要刷新
- 尝试使用 `dupan-music api list-files` 确认文件是否可访问

### 8.3 命令行显示乱码

**问题**：在某些终端中显示中文乱码。

**解决方案**：
- 确保终端支持 UTF-8 编码
- 设置环境变量：`export PYTHONIOENCODING=utf-8`
- 在 Windows 中，使用 `chcp 65001` 命令切换到 UTF-8 编码

### 8.4 播放列表文件丢失

**问题**：之前创建的播放列表找不到了。

**解决方案**：
- 播放列表文件存储在 `~/.dupan/playlists/` 目录下
- 检查该目录是否存在并有权限访问
- 如果有备份，可以使用 `dupan playlist import-playlist` 恢复

### 8.5 内存使用过高

**问题**：程序运行时内存占用过高。

**解决方案**：
- 减小播放列表大小
- 使用 `--limit` 选项限制返回结果数量
- 更新到最新版本，可能包含内存优化
- 检查是否有内存泄漏，可以提交 issue 报告

### 8.6 跨平台兼容性问题

**问题**：在不同操作系统上行为不一致。

**解决方案**：
- 确保使用最新版本
- 检查是否安装了所有依赖
- Windows 用户可能需要额外安装 VLC 媒体播放器
- 报告具体兼容性问题，帮助改进程序
