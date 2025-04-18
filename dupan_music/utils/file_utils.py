#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件工具模块
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple


def ensure_dir(directory: str) -> None:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节）
    """
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0


def get_file_md5(file_path: str) -> str:
    """
    获取文件MD5
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件MD5
    """
    if not os.path.exists(file_path):
        return ""
    
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件扩展名
    """
    return os.path.splitext(file_path)[1].lower()


def get_file_name(file_path: str) -> str:
    """
    获取文件名（不含扩展名）
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件名
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_name_with_extension(file_path: str) -> str:
    """
    获取文件名（含扩展名）
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件名
    """
    return os.path.basename(file_path)


def remove_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        return False


def remove_dir(directory: str) -> bool:
    """
    删除目录
    
    Args:
        directory: 目录路径
        
    Returns:
        bool: 是否成功
    """
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        return True
    except Exception:
        return False


def list_files(directory: str, recursive: bool = False) -> List[str]:
    """
    列出目录下的文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归
        
    Returns:
        List[str]: 文件列表
    """
    if not os.path.exists(directory):
        return []
    
    if recursive:
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
    else:
        return [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, filename))
        ]


def list_dirs(directory: str, recursive: bool = False) -> List[str]:
    """
    列出目录下的子目录
    
    Args:
        directory: 目录路径
        recursive: 是否递归
        
    Returns:
        List[str]: 目录列表
    """
    if not os.path.exists(directory):
        return []
    
    if recursive:
        dirs = []
        for root, dirnames, _ in os.walk(directory):
            for dirname in dirnames:
                dirs.append(os.path.join(root, dirname))
        return dirs
    else:
        return [
            os.path.join(directory, dirname)
            for dirname in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, dirname))
        ]


def copy_file(src: str, dst: str) -> bool:
    """
    复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保目标目录存在
        ensure_dir(os.path.dirname(dst))
        
        # 复制文件
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def move_file(src: str, dst: str) -> bool:
    """
    移动文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保目标目录存在
        ensure_dir(os.path.dirname(dst))
        
        # 移动文件
        shutil.move(src, dst)
        return True
    except Exception:
        return False


def read_file(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 编码
        
    Returns:
        Optional[str]: 文件内容
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception:
        return None


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径
        content: 内容
        encoding: 编码
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 写入文件
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def append_file(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    追加文件内容
    
    Args:
        file_path: 文件路径
        content: 内容
        encoding: 编码
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 追加文件
        with open(file_path, "a", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def read_binary_file(file_path: str) -> Optional[bytes]:
    """
    读取二进制文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        Optional[bytes]: 文件内容
    """
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception:
        return None


def write_binary_file(file_path: str, content: bytes) -> bool:
    """
    写入二进制文件内容
    
    Args:
        file_path: 文件路径
        content: 内容
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 写入文件
        with open(file_path, "wb") as f:
            f.write(content)
        return True
    except Exception:
        return False


def get_temp_dir() -> str:
    """
    获取临时目录
    
    Returns:
        str: 临时目录
    """
    import tempfile
    return tempfile.gettempdir()


def get_temp_file(suffix: str = "") -> str:
    """
    获取临时文件
    
    Args:
        suffix: 后缀
        
    Returns:
        str: 临时文件路径
    """
    import tempfile
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def human_readable_size(size_bytes: int) -> str:
    """
    人类可读的文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        str: 人类可读的文件大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_name[i]}"

# 为了兼容性，提供format_size作为human_readable_size的别名
format_size = human_readable_size


def split_file(file_path: str, chunk_size: int, output_dir: Optional[str] = None) -> List[str]:
    """
    分割文件
    
    Args:
        file_path: 文件路径
        chunk_size: 分块大小（字节）
        output_dir: 输出目录
        
    Returns:
        List[str]: 分块文件路径列表
    """
    if not os.path.exists(file_path):
        return []
    
    # 默认输出到同一目录
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    # 确保输出目录存在
    ensure_dir(output_dir)
    
    # 文件名
    file_name = get_file_name(file_path)
    file_ext = get_file_extension(file_path)
    
    # 分块文件列表
    chunk_files = []
    
    # 读取文件并分块
    with open(file_path, "rb") as f:
        i = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # 分块文件路径
            chunk_file = os.path.join(output_dir, f"{file_name}.{i:03d}{file_ext}")
            
            # 写入分块
            with open(chunk_file, "wb") as cf:
                cf.write(chunk)
            
            # 添加到列表
            chunk_files.append(chunk_file)
            i += 1
    
    return chunk_files


def merge_files(file_paths: List[str], output_file: str) -> bool:
    """
    合并文件
    
    Args:
        file_paths: 文件路径列表
        output_file: 输出文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保输出目录存在
        ensure_dir(os.path.dirname(output_file))
        
        # 合并文件
        with open(output_file, "wb") as out:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        out.write(f.read())
        
        return True
    except Exception:
        return False
