import os
from .path_utils import is_path_allowed, normalize_path
from .config import WORKDIR_ROOT

def write_to_file(filepath, content, overwrite=True):
    """写入文件（支持覆盖或追加）
    
    Args:
        filepath: 文件路径
        content: 要写入的内容
        overwrite: 是否覆盖原有内容 (True=覆盖, False=追加)
    """
    # 标准化路径
    full_path = normalize_path(filepath)
    
    # 检查权限
    allowed, base_path = is_path_allowed(full_path)
    if not allowed:
        return f"错误：无权在此位置写入文件。只能在默认工作目录 {WORKDIR_ROOT} 内操作。\n提示：如需使用外部路径，请联系管理员添加到白名单。"
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # 写入文件
        mode = 'w' if overwrite else 'a'
        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        # 返回相对路径（更友好）
        if full_path.startswith(os.path.abspath(WORKDIR_ROOT)):
            display_path = os.path.relpath(full_path, WORKDIR_ROOT)
            return f"文件已成功{'覆盖' if overwrite else '追加'}写入: {display_path} (默认工作目录)"
        else:
            return f"文件已成功{'覆盖' if overwrite else '追加'}写入: {full_path} (外部路径)"
    except Exception as e:
        return f"写入文件失败: {str(e)}"
