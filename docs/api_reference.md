# 百度盘音乐命令行播放器 API 参考文档

本文档提供了百度盘音乐命令行播放器的 API 参考，包括各个模块的类、方法和函数的详细说明。

## 目录

1. [认证模块 (auth.py)](#1-认证模块-authpy)
2. [API模块 (api.py)](#2-api模块-apipy)
3. [播放列表模块 (playlist.py)](#3-播放列表模块-playlistpy)
4. [播放器模块 (player.py)](#4-播放器模块-playerpy)
5. [配置模块 (config.py)](#5-配置模块-configpy)
6. [工具模块 (utils/)](#6-工具模块-utils)
7. [命令行接口模块 (cli.py)](#7-命令行接口模块-clipy)

## 1. 认证模块 (auth.py)

### BaiduPanAuth

百度网盘认证类，负责处理用户登录、令牌管理等认证相关功能。

#### 构造函数

```python
def __init__(self, config)
```

- **参数**
  - `config`: Config 对象，配置信息

#### 方法

##### get_login_url

```python
def get_login_url(self) -> str
```

- **描述**: 获取登录URL
- **返回值**: 登录URL字符串

##### get_device_code

```python
def get_device_code(self) -> Dict[str, Any]
```

- **描述**: 获取设备码，用于扫码登录
- **返回值**: 包含设备码信息的字典

##### get_qrcode

```python
def get_qrcode(self, device_code: str) -> str
```

- **描述**: 生成二维码
- **参数**
  - `device_code`: 设备码
- **返回值**: 二维码字符串

##### poll_authorization

```python
def poll_authorization(self, device_code: str, interval: int, expires_in: int) -> Dict[str, Any]
```

- **描述**: 轮询授权结果
- **参数**
  - `device_code`: 设备码
  - `interval`: 轮询间隔（秒）
  - `expires_in`: 过期时间（秒）
- **返回值**: 授权结果字典

##### set_token

```python
def set_token(self, access_token: str, refresh_token: str, expires_in: int) -> None
```

- **描述**: 设置令牌
- **参数**
  - `access_token`: 访问令牌
  - `refresh_token`: 刷新令牌
  - `expires_in`: 过期时间（秒）

##### refresh_token

```python
def refresh_token(self) -> bool
```

- **描述**: 刷新令牌
- **返回值**: 是否成功

##### is_authenticated

```python
def is_authenticated(self) -> bool
```

- **描述**: 检查是否已认证
- **返回值**: 是否已认证

##### get_access_token

```python
def get_access_token(self) -> str
```

- **描述**: 获取访问令牌
- **返回值**: 访问令牌字符串

##### get_refresh_token

```python
def get_refresh_token(self) -> str
```

- **描述**: 获取刷新令牌
- **返回值**: 刷新令牌字符串

##### logout

```python
def logout(self) -> bool
```

- **描述**: 退出登录
- **返回值**: 是否成功

## 2. API模块 (api.py)

### BaiduPanAPI

百度网盘API封装类，提供对百度网盘API的访问。

#### 构造函数

```python
def __init__(self, auth)
```

- **参数**
  - `auth`: BaiduPanAuth 对象，认证信息

#### 方法

##### list_files

```python
def list_files(self, dir_path: str, order: str = "name", desc: bool = False, limit: int = 1000) -> List[Dict[str, Any]]
```

- **描述**: 列出指定目录下的文件
- **参数**
  - `dir_path`: 目录路径
  - `order`: 排序方式（name, size, time）
  - `desc`: 是否降序
  - `limit`: 返回数量限制
- **返回值**: 文件列表

##### search_files

```python
def search_files(self, keyword: str, dir_path: str = "/", recursion: bool = True, limit: int = 1000) -> List[Dict[str, Any]]
```

- **描述**: 搜索文件
- **参数**
  - `keyword`: 关键词
  - `dir_path`: 搜索目录
  - `recursion`: 是否递归搜索
  - `limit`: 返回数量限制
- **返回值**: 文件列表

##### get_file_info

```python
def get_file_info(self, fs_id: int) -> Dict[str, Any]
```

- **描述**: 获取文件信息
- **参数**
  - `fs_id`: 文件ID
- **返回值**: 文件信息字典

##### get_download_link

```python
def get_download_link(self, fs_id: int) -> str
```

- **描述**: 获取下载链接
- **参数**
  - `fs_id`: 文件ID
- **返回值**: 下载链接字符串

##### filter_audio_files

```python
def filter_audio_files(self, files: List[Dict[str, Any]], supported_formats: List[str] = None) -> List[Dict[str, Any]]
```

- **描述**: 过滤音频文件
- **参数**
  - `files`: 文件列表
  - `supported_formats`: 支持的格式列表
- **返回值**: 过滤后的文件列表

## 3. 播放列表模块 (playlist.py)

### PlaylistManager

播放列表管理类，负责播放列表的创建、删除、修改等操作。

#### 构造函数

```python
def __init__(self, api, playlist_dir: str = None)
```

- **参数**
  - `api`: BaiduPanAPI 对象
  - `playlist_dir`: 播放列表目录

#### 方法

##### create_playlist

```python
def create_playlist(self, name: str) -> bool
```

- **描述**: 创建播放列表
- **参数**
  - `name`: 播放列表名称
- **返回值**: 是否成功

##### delete_playlist

```python
def delete_playlist(self, name: str) -> bool
```

- **描述**: 删除播放列表
- **参数**
  - `name`: 播放列表名称
- **返回值**: 是否成功

##### get_playlist

```python
def get_playlist(self, name: str) -> Dict[str, Any]
```

- **描述**: 获取播放列表
- **参数**
  - `name`: 播放列表名称
- **返回值**: 播放列表字典

##### list_playlists

```python
def list_playlists(self) -> List[str]
```

- **描述**: 列出所有播放列表
- **返回值**: 播放列表名称列表

##### add_files_to_playlist

```python
def add_files_to_playlist(self, name: str, file_paths: List[str]) -> bool
```

- **描述**: 添加文件到播放列表
- **参数**
  - `name`: 播放列表名称
  - `file_paths`: 文件路径列表
- **返回值**: 是否成功

##### remove_files_from_playlist

```python
def remove_files_from_playlist(self, name: str, indices: List[int]) -> bool
```

- **描述**: 从播放列表中移除文件
- **参数**
  - `name`: 播放列表名称
  - `indices`: 文件索引列表
- **返回值**: 是否成功

##### sort_playlist

```python
def sort_playlist(self, name: str, key: str = "name", reverse: bool = False) -> bool
```

- **描述**: 排序播放列表
- **参数**
  - `name`: 播放列表名称
  - `key`: 排序键（name, size, time）
  - `reverse`: 是否降序
- **返回值**: 是否成功

##### add_to_recent

```python
def add_to_recent(self, file_info: Dict[str, Any]) -> bool
```

- **描述**: 添加到最近播放
- **参数**
  - `file_info`: 文件信息
- **返回值**: 是否成功

##### export_playlist

```python
def export_playlist(self, name: str, export_path: str) -> bool
```

- **描述**: 导出播放列表
- **参数**
  - `name`: 播放列表名称
  - `export_path`: 导出路径
- **返回值**: 是否成功

##### import_playlist

```python
def import_playlist(self, import_path: str) -> bool
```

- **描述**: 导入播放列表
- **参数**
  - `import_path`: 导入路径
- **返回值**: 是否成功

## 4. 播放器模块 (player.py)

### AudioPlayer

音频播放器类，负责音频的播放、暂停、切换等操作。

#### 构造函数

```python
def __init__(self, api, playlist_manager)
```

- **参数**
  - `api`: BaiduPanAPI 对象
  - `playlist_manager`: PlaylistManager 对象

#### 方法

##### load_playlist

```python
def load_playlist(self, playlist_name: str) -> bool
```

- **描述**: 加载播放列表
- **参数**
  - `playlist_name`: 播放列表名称
- **返回值**: 是否成功

##### play

```python
def play(self, index: int = None) -> bool
```

- **描述**: 播放
- **参数**
  - `index`: 播放索引，默认为当前索引
- **返回值**: 是否成功

##### pause

```python
def pause(self) -> bool
```

- **描述**: 暂停
- **返回值**: 是否成功

##### resume

```python
def resume(self) -> bool
```

- **描述**: 恢复播放
- **返回值**: 是否成功

##### stop

```python
def stop(self) -> bool
```

- **描述**: 停止
- **返回值**: 是否成功

##### next

```python
def next(self) -> bool
```

- **描述**: 下一曲
- **返回值**: 是否成功

##### previous

```python
def previous(self) -> bool
```

- **描述**: 上一曲
- **返回值**: 是否成功

##### set_volume

```python
def set_volume(self, volume: int) -> bool
```

- **描述**: 设置音量
- **参数**
  - `volume`: 音量（0-100）
- **返回值**: 是否成功

##### get_volume

```python
def get_volume(self) -> int
```

- **描述**: 获取音量
- **返回值**: 音量（0-100）

##### is_playing

```python
def is_playing(self) -> bool
```

- **描述**: 是否正在播放
- **返回值**: 是否正在播放

##### get_current_position

```python
def get_current_position(self) -> int
```

- **描述**: 获取当前播放位置（毫秒）
- **返回值**: 当前播放位置

##### get_duration

```python
def get_duration(self) -> int
```

- **描述**: 获取当前曲目时长（毫秒）
- **返回值**: 当前曲目时长

##### get_current_track

```python
def get_current_track(self) -> Dict[str, Any]
```

- **描述**: 获取当前曲目信息
- **返回值**: 当前曲目信息字典

## 5. 配置模块 (config.py)

### Config

配置类，负责配置的加载、保存等操作。

#### 构造函数

```python
def __init__(self, config_file: str = None)
```

- **参数**
  - `config_file`: 配置文件路径

#### 方法

##### get

```python
def get(self, key: str, default: Any = None) -> Any
```

- **描述**: 获取配置
- **参数**
  - `key`: 配置键
  - `default`: 默认值
- **返回值**: 配置值

##### set

```python
def set(self, key: str, value: Any) -> None
```

- **描述**: 设置配置
- **参数**
  - `key`: 配置键
  - `value`: 配置值

##### save

```python
def save(self) -> bool
```

- **描述**: 保存配置
- **返回值**: 是否成功

##### reset

```python
def reset(self, key: Optional[str] = None) -> None
```

- **描述**: 重置配置
- **参数**
  - `key`: 配置键，如果为 None，则重置所有配置

##### get_all

```python
def get_all(self) -> Dict[str, Any]
```

- **描述**: 获取所有配置
- **返回值**: 所有配置字典

##### get_config_file

```python
def get_config_file(self) -> str
```

- **描述**: 获取配置文件路径
- **返回值**: 配置文件路径

## 6. 工具模块 (utils/)

### logger.py

#### setup_logger

```python
def setup_logger(name: str = None, level: str = "INFO", log_file: str = None, log_format: str = None, date_format: str = None) -> logging.Logger
```

- **描述**: 设置日志记录器
- **参数**
  - `name`: 日志记录器名称
  - `level`: 日志级别
  - `log_file`: 日志文件路径
  - `log_format`: 日志格式
  - `date_format`: 日期格式
- **返回值**: 日志记录器对象

### file_utils.py

#### ensure_dir

```python
def ensure_dir(path: str) -> bool
```

- **描述**: 确保目录存在
- **参数**
  - `path`: 目录路径
- **返回值**: 是否成功

#### get_file_extension

```python
def get_file_extension(path: str) -> str
```

- **描述**: 获取文件扩展名
- **参数**
  - `path`: 文件路径
- **返回值**: 文件扩展名

#### is_audio_file

```python
def is_audio_file(path: str, supported_formats: List[str] = None) -> bool
```

- **描述**: 检查是否为音频文件
- **参数**
  - `path`: 文件路径
  - `supported_formats`: 支持的格式列表
- **返回值**: 是否为音频文件

## 7. 命令行接口模块 (cli.py)

### auth/cli.py

#### login

```python
@click.command()
@click.option("--qr/--no-qr", default=True, help="是否使用二维码登录")
@click.pass_context
def login(ctx, qr)
```

- **描述**: 登录命令
- **参数**
  - `ctx`: Click 上下文
  - `qr`: 是否使用二维码登录

#### logout

```python
@click.command()
@click.pass_context
def logout(ctx)
```

- **描述**: 退出登录命令
- **参数**
  - `ctx`: Click 上下文

#### status

```python
@click.command()
@click.pass_context
def status(ctx)
```

- **描述**: 查看登录状态命令
- **参数**
  - `ctx`: Click 上下文

### api/cli.py

#### list_files

```python
@click.command()
@click.argument("path", default="/")
@click.option("--order", "-o", type=click.Choice(["name", "size", "time"]), default="name", help="排序方式")
@click.option("--desc/--asc", default=False, help="是否降序排列")
@click.option("--limit", "-l", type=int, default=1000, help="返回数量限制")
@click.pass_context
def list_files(ctx, path, order, desc, limit)
```

- **描述**: 列出文件命令
- **参数**
  - `ctx`: Click 上下文
  - `path`: 目录路径
  - `order`: 排序方式
  - `desc`: 是否降序
  - `limit`: 返回数量限制

#### search

```python
@click.command()
@click.argument("keyword")
@click.option("--path", "-p", default="/", help="搜索路径")
@click.option("--recursion/--no-recursion", default=True, help="是否递归搜索")
@click.option("--limit", "-l", type=int, default=1000, help="返回数量限制")
@click.pass_context
def search(ctx, keyword, path, recursion, limit)
```

- **描述**: 搜索文件命令
- **参数**
  - `ctx`: Click 上下文
  - `keyword`: 关键词
  - `path`: 搜索路径
  - `recursion`: 是否递归搜索
  - `limit`: 返回数量限制

### playlist/cli.py

#### list_playlists

```python
@click.command()
@click.pass_context
def list_playlists(ctx)
```

- **描述**: 列出播放列表命令
- **参数**
  - `ctx`: Click 上下文

#### create_playlist

```python
@click.command()
@click.argument("name")
@click.pass_context
def create_playlist(ctx, name)
```

- **描述**: 创建播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称

#### delete_playlist

```python
@click.command()
@click.argument("name")
@click.pass_context
def delete_playlist(ctx, name)
```

- **描述**: 删除播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称

#### show_playlist

```python
@click.command()
@click.argument("name")
@click.pass_context
def show_playlist(ctx, name)
```

- **描述**: 显示播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称

#### add_to_playlist

```python
@click.command()
@click.argument("name")
@click.argument("file_paths", nargs=-1, required=True)
@click.pass_context
def add_to_playlist(ctx, name, file_paths)
```

- **描述**: 添加文件到播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称
  - `file_paths`: 文件路径列表

#### remove_from_playlist

```python
@click.command()
@click.argument("name")
@click.argument("indices", nargs=-1, type=int, required=True)
@click.pass_context
def remove_from_playlist(ctx, name, indices)
```

- **描述**: 从播放列表中移除文件命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称
  - `indices`: 文件索引列表

#### sort_playlist

```python
@click.command()
@click.argument("name")
@click.option("--key", "-k", type=click.Choice(["name", "size", "time"]), default="name", help="排序键")
@click.option("--reverse/--no-reverse", default=False, help="是否降序")
@click.pass_context
def sort_playlist(ctx, name, key, reverse)
```

- **描述**: 排序播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称
  - `key`: 排序键
  - `reverse`: 是否降序

#### export_playlist

```python
@click.command()
@click.argument("name")
@click.argument("export_path")
@click.pass_context
def export_playlist(ctx, name, export_path)
```

- **描述**: 导出播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `name`: 播放列表名称
  - `export_path`: 导出路径

#### import_playlist

```python
@click.command()
@click.argument("import_path")
@click.pass_context
def import_playlist(ctx, import_path)
```

- **描述**: 导入播放列表命令
- **参数**
  - `ctx`: Click 上下文
  - `import_path`: 导入路径

### player/cli.py

#### play

```python
@click.command()
@click.argument("playlist_name")
@click.option("--index", "-i", type=int, help="播放索引")
@click.pass_context
def play(ctx, playlist_name, index)
```

- **描述**: 播放命令
- **参数**
  - `ctx`: Click 上下文
  - `playlist_name`: 播放列表名称
  - `index`: 播放索引

#### pause

```python
@click.command()
@click.pass_context
def pause(ctx)
```

- **描述**: 暂停命令
- **参数**
  - `ctx`: Click 上下文

#### resume

```python
@click.command()
@click.pass_context
def resume(ctx)
```

- **描述**: 恢复播放命令
- **参数**
  - `ctx`: Click 上下文

#### stop

```python
@click.command()
@click.pass_context
def stop(ctx)
```

- **描述**: 停止命令
- **参数**
  - `ctx`: Click 上下文

#### next_track

```python
@click.command()
@click.pass_context
def next_track(ctx)
```

- **描述**: 下一曲命令
- **参数**
  - `ctx`: Click 上下文

#### previous_track

```python
@click.command()
@click.pass_context
def previous_track(ctx)
```

- **描述**: 上一曲命令
- **参数**
  - `ctx`: Click 上下文

#### volume

```python
@click.command()
@click.argument("level", type=int, required=False)
@click.pass_context
def volume(ctx, level)
```

- **描述**: 音量命令
- **参数**
  - `ctx`: Click 上下文
  - `level`: 音量级别（0-100）

#### status

```python
@click.command()
@click.pass_context
def status(ctx)
```

- **描述**: 查看播放状态命令
- **参数**
  - `ctx`: Click 上下文
