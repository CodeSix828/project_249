import os
from pathlib import Path
from .config import WORKDIR_ROOT, ALLOWED_EXTERNAL_PATHS

def is_path_allowed(filepath):
    """检查路径是否允许访问"""
    # 转换为绝对路径
    abs_path = os.path.abspath(filepath)
    abs_workdir = os.path.abspath(WORKDIR_ROOT)
    
    # 1. 检查是否在默认工作目录内
    if abs_path.startswith(abs_workdir):
        return True, WORKDIR_ROOT
    
    # 2. 检查是否在白名单内
    for allowed_path in ALLOWED_EXTERNAL_PATHS:
        if abs_path.startswith(os.path.abspath(allowed_path)):
            return True, allowed_path
    
    # 3. 不允许访问
    return False, None

def normalize_path(filepath):
    """标准化路径，支持相对路径和绝对路径"""
    if os.path.isabs(filepath):
        # 绝对路径：直接使用
        return filepath
    else:
        # 相对路径：基于默认工作目录
        return os.path.join(WORKDIR_ROOT, filepath)