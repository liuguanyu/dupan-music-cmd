# 百度盘音乐命令行播放器

一个基于Python的百度网盘音乐命令行播放器，支持Windows、Mac和主流Linux系统。

## 功能特点

- 通过命令行方式登录百度云盘，支持扫码登录
- 管理和播放百度云盘中的音乐文件
- 创建和管理播放列表
- 支持多种音频格式：mp3、m4a、ogg、wav、flac、aiff等
- 播放控制：播放、暂停、下一曲、上一曲、音量调节等
- 自动记录最近播放的音乐
- 美化的命令行界面
- 交互式shell模式，支持命令自动补全和历史记录

## 安装要求

- Python 3.8 或更高版本
- 外部依赖：
  - VLC媒体播放器（用于音频播放）
  - ffmpeg（用于音频处理）

### 安装VLC媒体播放器

#### Windows
1. 访问 [VLC官网](https://www.videolan.org/vlc/index.html) 下载并安装VLC
2. 确保VLC安装路径已添加到系统环境变量PATH中

#### macOS
```bash
brew install vlc
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install vlc
```

### 安装ffmpeg

#### Windows
1. 访问 [ffmpeg官网](https://ffmpeg.org/download.html) 下载
2. 解压并将bin目录添加到系统环境变量PATH中

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

## 安装

### 从PyPI安装（推荐）

```bash
pip install dupan-music
```

### 从源码安装

```bash
git clone https://github.com/example/dupan-music.git
cd dupan-music
pip install -e .
```

## 使用方法

### 登录百度云盘

```bash
dupan-music auth login
```

### 列出播放列表

```bash
dupan-music playlist list
```

### 播放音乐

```bash
dupan-music player play [播放列表名称]
```

### 创建播放列表

```bash
dupan-music playlist create <播放列表名称>
```

### 添加文件到播放列表

```bash
dupan-music playlist add <播放列表名称> <文件路径1> [文件路径2 ...]
```

### 删除播放列表

```bash
dupan-music playlist delete <播放列表名称>
```

### 启动交互式shell

```bash
dupan-music shell
```

交互式shell提供了以下功能：
- 命令自动补全（按Tab键）
- 历史命令记录和搜索（按上下方向键或Ctrl+R）
- 路径自动补全
- 彩色输出和美化界面
- 实时播放状态显示在提示符中

#### 交互式shell中可用的命令

```
# 查看可用命令
help

# 查看特定命令的帮助
help play

# 认证命令
login           # 登录百度网盘
logout          # 退出登录
status          # 查看登录状态

# 文件操作
list-files /音乐  # 列出指定目录的文件
search 周杰伦     # 搜索文件

# 播放列表管理
create-playlist 我的最爱                          # 创建播放列表
list-playlists                                  # 列出所有播放列表
show-playlist 我的最爱                            # 显示播放列表内容
add-to-playlist 我的最爱 /音乐/周杰伦/稻香.mp3       # 添加文件到播放列表
remove-from-playlist 我的最爱 0                   # 从播放列表中移除文件
sort-playlist 我的最爱 --key name                 # 排序播放列表
export-playlist 我的最爱 ~/我的最爱.json            # 导出播放列表
import-playlist ~/我的最爱.json                   # 导入播放列表

# 播放控制
play 我的最爱     # 播放指定播放列表
pause           # 暂停播放
resume          # 恢复播放
stop            # 停止播放
next            # 下一曲
previous        # 上一曲
volume 80       # 设置音量
status          # 查看播放状态

# 退出Shell
exit
quit
```

#### 交互式shell配置

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

## 许可证

MIT

## 贡献

欢迎提交问题和拉取请求！
