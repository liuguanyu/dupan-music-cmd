#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试文件工具模块
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from dupan_music.utils.file_utils import (
    ensure_dir, get_file_size, get_file_md5, get_file_extension,
    get_file_name, get_file_name_with_extension, remove_file, remove_dir,
    list_files, list_dirs, copy_file, move_file, read_file, write_file,
    append_file, read_binary_file, write_binary_file, get_temp_dir,
    get_temp_file, human_readable_size, format_size, split_file, merge_files
)


class TestFileUtils:
    """测试文件工具模块"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_file(self):
        """创建临时文件"""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)
    
    def test_ensure_dir(self, temp_dir):
        """测试确保目录存在"""
        # 测试创建新目录
        new_dir = os.path.join(temp_dir, "new_dir")
        ensure_dir(new_dir)
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
        
        # 测试已存在的目录
        ensure_dir(new_dir)  # 不应该报错
        assert os.path.exists(new_dir)
        
        # 测试嵌套目录
        nested_dir = os.path.join(temp_dir, "parent", "child", "grandchild")
        ensure_dir(nested_dir)
        assert os.path.exists(nested_dir)
        assert os.path.isdir(nested_dir)
    
    def test_get_file_size(self, temp_file):
        """测试获取文件大小"""
        # 写入一些内容
        with open(temp_file, "w") as f:
            f.write("Hello, World!")
        
        # 测试获取文件大小
        size = get_file_size(temp_file)
        assert size == 13  # "Hello, World!" 的长度
        
        # 测试不存在的文件
        assert get_file_size("non_existent_file.txt") == 0
    
    def test_get_file_md5(self, temp_file):
        """测试获取文件MD5"""
        # 写入一些内容
        with open(temp_file, "w") as f:
            f.write("Hello, World!")
        
        # 测试获取文件MD5
        md5 = get_file_md5(temp_file)
        assert md5 == "65a8e27d8879283831b664bd8b7f0ad4"  # "Hello, World!" 的MD5
        
        # 测试不存在的文件
        assert get_file_md5("non_existent_file.txt") == ""
    
    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        assert get_file_extension("test.txt") == ".txt"
        assert get_file_extension("test.tar.gz") == ".gz"
        assert get_file_extension("test") == ""
        assert get_file_extension("/path/to/test.jpg") == ".jpg"
    
    def test_get_file_name(self):
        """测试获取文件名（不含扩展名）"""
        assert get_file_name("test.txt") == "test"
        assert get_file_name("test.tar.gz") == "test.tar"
        assert get_file_name("test") == "test"
        assert get_file_name("/path/to/test.jpg") == "test"
    
    def test_get_file_name_with_extension(self):
        """测试获取文件名（含扩展名）"""
        assert get_file_name_with_extension("test.txt") == "test.txt"
        assert get_file_name_with_extension("test.tar.gz") == "test.tar.gz"
        assert get_file_name_with_extension("test") == "test"
        assert get_file_name_with_extension("/path/to/test.jpg") == "test.jpg"
    
    def test_remove_file(self, temp_file):
        """测试删除文件"""
        # 确保文件存在
        assert os.path.exists(temp_file)
        
        # 测试删除文件
        assert remove_file(temp_file)
        assert not os.path.exists(temp_file)
        
        # 测试删除不存在的文件
        assert remove_file(temp_file)  # 应该返回True，不报错
    
    def test_remove_dir(self, temp_dir):
        """测试删除目录"""
        # 创建嵌套目录和文件
        nested_dir = os.path.join(temp_dir, "nested")
        os.makedirs(nested_dir)
        with open(os.path.join(nested_dir, "test.txt"), "w") as f:
            f.write("test")
        
        # 确保目录存在
        assert os.path.exists(temp_dir)
        assert os.path.exists(nested_dir)
        
        # 测试删除目录
        assert remove_dir(temp_dir)
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(nested_dir)
        
        # 测试删除不存在的目录
        assert remove_dir(temp_dir)  # 应该返回True，不报错
    
    def test_list_files(self, temp_dir):
        """测试列出目录下的文件"""
        # 创建一些文件和目录
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "file2.txt")
        nested_dir = os.path.join(temp_dir, "nested")
        os.makedirs(nested_dir)
        file3 = os.path.join(nested_dir, "file3.txt")
        
        # 写入一些内容
        for file_path in [file1, file2, file3]:
            with open(file_path, "w") as f:
                f.write("test")
        
        # 测试非递归列出文件
        files = list_files(temp_dir)
        assert len(files) == 2
        assert file1 in files
        assert file2 in files
        assert file3 not in files
        
        # 测试递归列出文件
        files = list_files(temp_dir, recursive=True)
        assert len(files) == 3
        assert file1 in files
        assert file2 in files
        assert file3 in files
        
        # 测试不存在的目录
        assert list_files("non_existent_dir") == []
    
    def test_list_dirs(self, temp_dir):
        """测试列出目录下的子目录"""
        # 创建一些目录
        dir1 = os.path.join(temp_dir, "dir1")
        dir2 = os.path.join(temp_dir, "dir2")
        nested_dir = os.path.join(dir1, "nested")
        
        # 创建目录
        for dir_path in [dir1, dir2, nested_dir]:
            os.makedirs(dir_path)
        
        # 测试非递归列出目录
        dirs = list_dirs(temp_dir)
        assert len(dirs) == 2
        assert dir1 in dirs
        assert dir2 in dirs
        assert nested_dir not in dirs
        
        # 测试递归列出目录
        dirs = list_dirs(temp_dir, recursive=True)
        assert len(dirs) == 3
        assert dir1 in dirs
        assert dir2 in dirs
        assert nested_dir in dirs
        
        # 测试不存在的目录
        assert list_dirs("non_existent_dir") == []
    
    def test_copy_file(self, temp_dir, temp_file):
        """测试复制文件"""
        # 写入一些内容
        with open(temp_file, "w") as f:
            f.write("Hello, World!")
        
        # 目标文件路径
        dest_file = os.path.join(temp_dir, "dest.txt")
        
        # 测试复制文件
        assert copy_file(temp_file, dest_file)
        assert os.path.exists(dest_file)
        
        # 验证内容
        with open(dest_file, "r") as f:
            content = f.read()
            assert content == "Hello, World!"
        
        # 测试复制到嵌套目录
        nested_file = os.path.join(temp_dir, "nested", "dest.txt")
        assert copy_file(temp_file, nested_file)
        assert os.path.exists(nested_file)
        
        # 测试复制不存在的文件
        assert not copy_file("non_existent_file.txt", dest_file)
    
    def test_move_file(self, temp_dir):
        """测试移动文件"""
        # 创建源文件
        src_file = os.path.join(temp_dir, "src.txt")
        with open(src_file, "w") as f:
            f.write("Hello, World!")
        
        # 目标文件路径
        dest_file = os.path.join(temp_dir, "dest.txt")
        
        # 测试移动文件
        assert move_file(src_file, dest_file)
        assert not os.path.exists(src_file)
        assert os.path.exists(dest_file)
        
        # 验证内容
        with open(dest_file, "r") as f:
            content = f.read()
            assert content == "Hello, World!"
        
        # 测试移动到嵌套目录
        nested_file = os.path.join(temp_dir, "nested", "dest.txt")
        assert move_file(dest_file, nested_file)
        assert not os.path.exists(dest_file)
        assert os.path.exists(nested_file)
        
        # 测试移动不存在的文件
        assert not move_file("non_existent_file.txt", dest_file)
    
    def test_read_write_file(self, temp_dir):
        """测试读写文件内容"""
        # 文件路径
        file_path = os.path.join(temp_dir, "test.txt")
        
        # 测试写入文件
        content = "Hello, World!"
        assert write_file(file_path, content)
        assert os.path.exists(file_path)
        
        # 测试读取文件
        read_content = read_file(file_path)
        assert read_content == content
        
        # 测试追加文件
        append_content = "\nAppended content"
        assert append_file(file_path, append_content)
        
        # 验证追加后的内容
        read_content = read_file(file_path)
        assert read_content == content + append_content
        
        # 测试读取不存在的文件
        assert read_file("non_existent_file.txt") is None
    
    def test_read_write_binary_file(self, temp_dir):
        """测试读写二进制文件内容"""
        # 文件路径
        file_path = os.path.join(temp_dir, "test.bin")
        
        # 测试写入二进制文件
        content = b"\x00\x01\x02\x03"
        assert write_binary_file(file_path, content)
        assert os.path.exists(file_path)
        
        # 测试读取二进制文件
        read_content = read_binary_file(file_path)
        assert read_content == content
        
        # 测试读取不存在的文件
        assert read_binary_file("non_existent_file.bin") is None
    
    def test_get_temp_dir(self):
        """测试获取临时目录"""
        temp_dir = get_temp_dir()
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
    
    def test_get_temp_file(self):
        """测试获取临时文件"""
        # 测试默认后缀
        temp_file = get_temp_file()
        assert os.path.exists(temp_file)
        assert os.path.isfile(temp_file)
        os.remove(temp_file)  # 清理
        
        # 测试自定义后缀
        temp_file = get_temp_file(".txt")
        assert os.path.exists(temp_file)
        assert os.path.isfile(temp_file)
        assert temp_file.endswith(".txt")
        os.remove(temp_file)  # 清理
    
    def test_human_readable_size(self):
        """测试人类可读的文件大小"""
        assert human_readable_size(0) == "0B"
        assert human_readable_size(1023) == "1023.00B"
        assert human_readable_size(1024) == "1.00KB"
        assert human_readable_size(1024 * 1024) == "1.00MB"
        assert human_readable_size(1024 * 1024 * 1024) == "1.00GB"
        
        # 测试format_size别名
        assert format_size(1024) == "1.00KB"
    
    def test_split_merge_files(self, temp_dir):
        """测试分割合并文件"""
        # 创建源文件
        src_file = os.path.join(temp_dir, "source.txt")
        content = "A" * 1000 + "B" * 1000 + "C" * 1000  # 3000字节
        with open(src_file, "w") as f:
            f.write(content)
        
        # 分割文件
        chunk_size = 1000  # 每个分块1000字节
        output_dir = os.path.join(temp_dir, "chunks")
        chunk_files = split_file(src_file, chunk_size, output_dir)
        
        # 验证分块
        assert len(chunk_files) == 3
        
        # 验证分块内容
        with open(chunk_files[0], "r") as f:
            assert f.read() == "A" * 1000
        with open(chunk_files[1], "r") as f:
            assert f.read() == "B" * 1000
        with open(chunk_files[2], "r") as f:
            assert f.read() == "C" * 1000
        
        # 合并文件
        merged_file = os.path.join(temp_dir, "merged.txt")
        assert merge_files(chunk_files, merged_file)
        
        # 验证合并后的内容
        with open(merged_file, "r") as f:
            assert f.read() == content
        
        # 测试分割不存在的文件
        assert split_file("non_existent_file.txt", 1000) == []
        
        # 测试合并空列表
        assert not merge_files([], merged_file)
