@echo off
:: 百度盘音乐命令行播放器安装脚本
:: 适用于Windows系统

echo 开始安装百度盘音乐命令行播放器...

:: 检查Python版本
echo 检查Python版本...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请安装Python 3.8或更高版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
for /f "tokens=1 delims=." %%i in ("%PYTHON_VERSION%") do set PYTHON_MAJOR=%%i
for /f "tokens=2 delims=." %%i in ("%PYTHON_VERSION%") do set PYTHON_MINOR=%%i

if %PYTHON_MAJOR% LSS 3 (
    echo 错误: 需要Python 3.8或更高版本，当前版本为%PYTHON_VERSION%
    pause
    exit /b 1
) else (
    if %PYTHON_MAJOR% EQU 3 (
        if %PYTHON_MINOR% LSS 8 (
            echo 错误: 需要Python 3.8或更高版本，当前版本为%PYTHON_VERSION%
            pause
            exit /b 1
        )
    )
)

echo Python版本检查通过: %PYTHON_VERSION%

:: 检查pip
echo 检查pip...
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到pip，请确保pip已正确安装
    pause
    exit /b 1
)

:: 检查外部依赖
echo 检查外部依赖...

:: 检查ffmpeg
where ffmpeg > nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到ffmpeg，某些音频格式可能无法正常播放
    echo 请从 https://ffmpeg.org/download.html 下载并安装ffmpeg
    echo 并确保将其添加到系统PATH环境变量中
    
    set /p CONTINUE=是否继续安装? (y/n): 
    if /i "%CONTINUE%" neq "y" (
        pause
        exit /b 1
    )
) else (
    echo ffmpeg已安装
)

:: 检查VLC
where vlc > nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到VLC，某些功能可能受限
    echo 请从 https://www.videolan.org/vlc/ 下载并安装VLC
    echo 并确保将其添加到系统PATH环境变量中
    
    set /p CONTINUE=是否继续安装? (y/n): 
    if /i "%CONTINUE%" neq "y" (
        pause
        exit /b 1
    )
) else (
    echo VLC已安装
)

:: 创建虚拟环境（可选）
set /p CREATE_VENV=是否创建虚拟环境? (y/n): 
if /i "%CREATE_VENV%" equ "y" (
    echo 创建虚拟环境...
    python -m venv venv
    
    call venv\Scripts\activate
    if %errorlevel% neq 0 (
        echo 无法激活虚拟环境，请手动激活
        pause
        exit /b 1
    )
    
    echo 虚拟环境已创建并激活
    set PIP_CMD=pip
) else (
    set PIP_CMD=pip
)

:: 安装依赖
echo 安装依赖...
%PIP_CMD% install --upgrade pip
%PIP_CMD% install -e .

:: 检查安装结果
if %errorlevel% neq 0 (
    echo 安装失败，请检查错误信息
    pause
    exit /b 1
) else (
    echo 百度盘音乐命令行播放器安装成功!
    echo 使用方法: dupan-music --help
)

:: 提示用户配置
echo 请确保在使用前配置您的凭据:
echo 1. 复制配置文件模板: copy dupan_music\config\credentials.example.py dupan_music\config\credentials.py
echo 2. 编辑配置文件，填入您的凭据

echo 安装完成!
pause
