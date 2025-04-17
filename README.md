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
dupan-music login
```

### 列出播放列表

```bash
dupan-music list
```

### 播放音乐

```bash
dupan-music play [播放列表名称]
```

### 创建播放列表

```bash
dupan-music create <播放列表名称>
```

### 添加文件到播放列表

```bash
dupan-music add <播放列表名称> <文件路径1> [文件路径2 ...]
```

### 删除播放列表

```bash
dupan-music delete <播放列表名称>
```

## 许可证

MIT

## 贡献

欢迎提交问题和拉取请求！
