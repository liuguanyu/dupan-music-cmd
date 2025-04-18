# 百度盘音乐命令行播放器 开发者指南

本文档提供了百度盘音乐命令行播放器的开发者指南，包括项目架构、开发环境设置、贡献指南等信息。

## 目录

1. [项目架构](#1-项目架构)
2. [开发环境设置](#2-开发环境设置)
3. [代码风格指南](#3-代码风格指南)
4. [测试指南](#4-测试指南)
5. [贡献指南](#5-贡献指南)
6. [扩展指南](#6-扩展指南)

## 1. 项目架构

项目采用模块化设计，主要分为以下几个模块：

### 1.1 核心模块

- **认证模块 (auth.py)**: 处理百度网盘的认证流程，包括登录、令牌管理等。
- **API模块 (api.py)**: 封装百度网盘API，提供文件列表、搜索、下载链接获取等功能。
- **播放列表模块 (playlist.py)**: 管理播放列表，包括创建、删除、添加文件、排序等操作。
- **播放器模块 (player.py)**: 处理音频播放，包括播放控制、音量调节、进度显示等功能。
- **配置模块 (config.py)**: 管理配置信息，包括加载、保存配置等操作。

### 1.2 工具模块

- **日志模块 (utils/logger.py)**: 提供日志记录功能。
- **文件工具模块 (utils/file_utils.py)**: 提供文件操作相关的工具函数。

### 1.3 命令行接口模块

- **主命令行模块 (main.py)**: 定义主命令行入口和子命令组。
- **认证命令行模块 (auth/cli.py)**: 提供认证相关的命令行接口。
- **API命令行模块 (api/cli.py)**: 提供API相关的命令行接口。
- **播放列表命令行模块 (playlist/cli.py)**: 提供播放列表相关的命令行接口。
- **播放器命令行模块 (player/cli.py)**: 提供播放器相关的命令行接口。

### 1.4 模块依赖关系

```
main.py
  ├── auth/cli.py
  │     └── auth.py
  ├── api/cli.py
  │     └── api.py
  ├── playlist/cli.py
  │     ├── playlist.py
  │     └── api.py
  └── player/cli.py
        ├── player.py
        ├── playlist.py
        └── api.py
```

## 2. 开发环境设置

### 2.1 环境要求

- Python 3.8+
- 外部依赖: ffmpeg

### 2.2 设置开发环境

1. 克隆代码库

```bash
git clone https://github.com/yourusername/dupan-music-cmd.git
cd dupan-music-cmd
```

2. 创建并激活虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 或使用 conda
conda create -n dupan-music python=3.8
conda activate dupan-music
```

3. 安装依赖

```bash
pip install -e .  # 以开发模式安装
```

4. 安装外部依赖

- **ffmpeg**: 用于音频处理
  - Linux: `sudo apt-get install ffmpeg`
  - Mac: `brew install ffmpeg`
  - Windows: 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载并添加到 PATH

### 2.3 配置开发环境

1. 复制配置模板

```bash
cp dupan_music/config/credentials.example.py dupan_music/config/credentials.py
```

2. 编辑配置文件，填入你的百度云API信息

```python
# dupan_music/config/credentials.py
CONFIG = {
  'app_id': 'your_app_id',
  'app_key': 'your_app_key',
  'secret_key': 'your_secret_key',
  'sign_key': 'your_sign_key',
  'redirect_uri': 'oob',
  'scope': 'basic,netdisk',
  'device_id': '',
  'device_name': '度盘读天下',
  'api_base_url': 'https://pan.baidu.com/rest/2.0',
  'oauth_url': 'https://openapi.baidu.com/oauth/2.0'
}
```

## 3. 代码风格指南

### 3.1 Python 风格指南

本项目遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南，主要规范包括：

- 缩进使用 4 个空格
- 行长度不超过 100 个字符
- 使用空行分隔函数和类
- 导入顺序: 标准库、第三方库、本地库
- 类名使用 CamelCase，函数和变量名使用 snake_case
- 常量使用大写字母和下划线

### 3.2 文档字符串

使用 Google 风格的文档字符串：

```python
def function_name(param1, param2):
    """函数简短描述。

    更详细的函数描述，可以多行。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 错误描述
    """
    pass
```

### 3.3 代码注释

- 使用行内注释解释复杂的代码逻辑
- 避免不必要的注释
- 保持注释与代码同步更新

### 3.4 类型提示

使用 Python 3.8+ 的类型提示功能：

```python
def greeting(name: str) -> str:
    return f"Hello {name}"
```

## 4. 测试指南

### 4.1 测试框架

本项目使用 pytest 作为测试框架。

### 4.2 测试目录结构

```
tests/
  ├── conftest.py           # pytest 配置和共享 fixtures
  ├── test_main.py          # 主模块测试
  ├── api/
  │     ├── test_api.py     # API 模块测试
  │     └── test_cli.py     # API CLI 模块测试
  ├── auth/
  │     ├── test_auth.py    # 认证模块测试
  │     └── test_cli.py     # 认证 CLI 模块测试
  ├── player/
  │     ├── test_player.py  # 播放器模块测试
  │     └── test_cli.py     # 播放器 CLI 模块测试
  ├── playlist/
  │     ├── test_playlist.py # 播放列表模块测试
  │     └── test_cli.py      # 播放列表 CLI 模块测试
  ├── config/
  │     └── test_config.py   # 配置模块测试
  ├── utils/
  │     ├── test_logger.py   # 日志模块测试
  │     └── test_file_utils.py # 文件工具模块测试
  └── integration/
        └── test_integration.py # 集成测试
```

### 4.3 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/api/test_api.py

# 运行特定测试函数
pytest tests/api/test_api.py::test_list_files

# 生成覆盖率报告
pytest --cov=dupan_music
```

### 4.4 编写测试

- 每个测试函数应该只测试一个功能点
- 使用 fixtures 设置测试环境
- 使用 mock 对象模拟外部依赖
- 使用断言验证结果

```python
def test_list_files(mock_api):
    # 设置 mock 对象的行为
    mock_api.return_value = [{"fs_id": 123, "path": "/test.mp3"}]
    
    # 调用被测试的函数
    result = list_files("/")
    
    # 验证结果
    assert len(result) == 1
    assert result[0]["fs_id"] == 123
```

## 5. 贡献指南

### 5.1 提交代码

1. Fork 代码库
2. 创建功能分支: `git checkout -b feature/your-feature-name`
3. 提交更改: `git commit -am 'Add some feature'`
4. 推送到分支: `git push origin feature/your-feature-name`
5. 提交 Pull Request

### 5.2 提交规范

提交信息格式：

```
<类型>: <描述>

[可选的详细描述]

[可选的相关 issue]
```

类型包括：
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码风格更改（不影响代码功能）
- refactor: 代码重构
- perf: 性能优化
- test: 添加测试
- chore: 构建过程或辅助工具的变动

例如：

```
feat: 添加播放列表导出功能

添加了将播放列表导出为 JSON 文件的功能，
用户可以通过命令行参数指定导出路径。

Closes #123
```

### 5.3 代码审查

- 代码审查将关注以下方面：
  - 功能正确性
  - 代码质量和风格
  - 测试覆盖率
  - 文档完整性

## 6. 扩展指南

### 6.1 添加新命令

1. 在相应的 cli.py 文件中定义新命令函数：

```python
@click.command()
@click.argument("arg1")
@click.option("--option1", help="选项描述")
@click.pass_context
def new_command(ctx, arg1, option1):
    """命令描述"""
    # 命令实现
    pass
```

2. 在相应的命令组中注册新命令：

```python
from .cli import new_command

def register_commands(group):
    group.add_command(new_command)
```

### 6.2 添加新模块

1. 创建新模块目录和文件：

```
dupan_music/
  └── new_module/
        ├── __init__.py
        ├── new_module.py  # 核心功能
        └── cli.py         # 命令行接口
```

2. 在 new_module.py 中实现核心功能：

```python
class NewModule:
    def __init__(self, api):
        self.api = api
        
    def some_function(self):
        # 实现功能
        pass
```

3. 在 cli.py 中实现命令行接口：

```python
import click
from ..api.api import BaiduPanAPI
from .new_module import NewModule

@click.group()
@click.pass_context
def new_module_cli(ctx):
    """新模块命令组描述"""
    api = ctx.obj.get("api")
    ctx.obj["new_module"] = NewModule(api)

@new_module_cli.command()
@click.pass_context
def some_command(ctx):
    """命令描述"""
    new_module = ctx.obj["new_module"]
    result = new_module.some_function()
    # 处理结果
```

4. 在 main.py 中注册新命令组：

```python
from .new_module.cli import new_module_cli

cli.add_command(new_module_cli)
```

### 6.3 支持新的音频格式

1. 在 player.py 中添加新格式支持：

```python
SUPPORTED_FORMATS = ["mp3", "m4a", "ogg", "wav", "flac", "aiff", "new_format"]

def play_file(self, file_path):
    # 检查文件格式
    ext = get_file_extension(file_path).lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}")
    
    # 根据格式选择播放方法
    if ext == "new_format":
        # 实现新格式的播放逻辑
        pass
    else:
        # 使用现有方法播放
        pass
```

2. 更新文件工具模块以识别新格式：

```python
def is_audio_file(path, supported_formats=None):
    if supported_formats is None:
        supported_formats = ["mp3", "m4a", "ogg", "wav", "flac", "aiff", "new_format"]
    ext = get_file_extension(path).lower()
    return ext in supported_formats
