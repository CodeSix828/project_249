import os
from .path_utils import is_path_allowed, normalize_path
from .config import WORKDIR_ROOT

def mkdir(path):
    """创建目录（仅允许在默认路径或白名单内）"""
    # 标准化路径
    full_path = normalize_path(path)
    
    # 检查权限
    allowed, base_path = is_path_allowed(full_path)
    if not allowed:
        return f"错误：无权在此位置创建目录。只能在默认工作目录 {WORKDIR_ROOT} 内操作。"
    
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"目录已创建: {full_path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}"





