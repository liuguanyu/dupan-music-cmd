#!/bin/bash

# 百度盘音乐命令行播放器安装脚本
# 适用于Linux和macOS系统

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始安装百度盘音乐命令行播放器...${NC}"

# 检查Python版本
echo -e "${YELLOW}检查Python版本...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${RED}错误: 需要Python 3.8或更高版本，当前版本为${PYTHON_VERSION}${NC}"
        exit 1
    else
        echo -e "${GREEN}Python版本检查通过: ${PYTHON_VERSION}${NC}"
        PYTHON_CMD="python3"
    fi
else
    echo -e "${RED}错误: 未找到Python 3，请安装Python 3.8或更高版本${NC}"
    exit 1
fi

# 检查pip
echo -e "${YELLOW}检查pip...${NC}"
if ! command -v pip3 &>/dev/null; then
    echo -e "${RED}错误: 未找到pip3，请安装pip${NC}"
    exit 1
fi

# 检查外部依赖
echo -e "${YELLOW}检查外部依赖...${NC}"

# 检查ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${RED}警告: 未找到ffmpeg，某些音频格式可能无法正常播放${NC}"
    echo -e "${YELLOW}请使用以下命令安装ffmpeg:${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}macOS: brew install ffmpeg${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install ffmpeg${NC}"
        echo -e "${YELLOW}CentOS/RHEL: sudo yum install ffmpeg${NC}"
        echo -e "${YELLOW}Fedora: sudo dnf install ffmpeg${NC}"
        echo -e "${YELLOW}Arch Linux: sudo pacman -S ffmpeg${NC}"
    fi
    
    read -p "是否继续安装? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}ffmpeg已安装${NC}"
fi

# 检查VLC
if ! command -v vlc &>/dev/null; then
    echo -e "${RED}警告: 未找到VLC，某些功能可能受限${NC}"
    echo -e "${YELLOW}请使用以下命令安装VLC:${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}macOS: brew install vlc${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install vlc${NC}"
        echo -e "${YELLOW}CentOS/RHEL: sudo yum install vlc${NC}"
        echo -e "${YELLOW}Fedora: sudo dnf install vlc${NC}"
        echo -e "${YELLOW}Arch Linux: sudo pacman -S vlc${NC}"
    fi
    
    read -p "是否继续安装? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}VLC已安装${NC}"
fi

# 创建虚拟环境（可选）
echo -e "${YELLOW}是否创建虚拟环境? (y/n)${NC}"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    $PYTHON_CMD -m venv venv
    
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source venv/bin/activate
    else
        echo -e "${RED}无法激活虚拟环境，请手动激活${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}虚拟环境已创建并激活${NC}"
    PIP_CMD="pip"
else
    PIP_CMD="pip3"
fi

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
$PIP_CMD install --upgrade pip
$PIP_CMD install -e .

# 检查安装结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}百度盘音乐命令行播放器安装成功!${NC}"
    echo -e "${YELLOW}使用方法: dupan-music --help${NC}"
else
    echo -e "${RED}安装失败，请检查错误信息${NC}"
    exit 1
fi

# 提示用户配置
echo -e "${YELLOW}请确保在使用前配置您的凭据:${NC}"
echo -e "${YELLOW}1. 复制配置文件模板: cp dupan_music/config/credentials.example.py dupan_music/config/credentials.py${NC}"
echo -e "${YELLOW}2. 编辑配置文件，填入您的凭据${NC}"

echo -e "${GREEN}安装完成!${NC}"
