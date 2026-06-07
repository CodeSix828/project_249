import os
from pathlib import Path
from .path_utils import normalize_path, is_path_allowed
from .config import WORKDIR_ROOT

def check_path(filepath, preview_lines=5, preview_full=False):
    """检测文件或文件夹是否存在及其详细信息
    
    Args:
        filepath: 要检测的路径（支持相对路径和绝对路径）
        preview_lines: 预览行数（默认5行）
        preview_full: 是否预览完整文件内容（默认False，仅在预览较小文件时有用）
    
    Returns:
        包含详细信息的字符串
    """
    # 标准化路径
    full_path = normalize_path(filepath)
    
    # 检查路径是否存在
    exists = os.path.exists(full_path)
    
    if not exists:
        return f"路径不存在: {full_path}\n提示：请检查路径是否正确"
    
    # 获取详细信息
    path_obj = Path(full_path)
    
    # 基本信息
    info = []
    info.append(f"路径: {full_path}")
    info.append(f"类型: {'目录' if path_obj.is_dir() else '文件' if path_obj.is_file() else '其他'}")
    info.append(f"存在: 是")
    
    # 大小（仅文件）
    if path_obj.is_file():
        size = path_obj.stat().st_size
        if size < 1024:
            size_str = f"{size} 字节"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        info.append(f"大小: {size_str}")
    
    # 权限信息
    info.append(f"可读: {'是' if os.access(full_path, os.R_OK) else '否'}")
    info.append(f"可写: {'是' if os.access(full_path, os.W_OK) else '否'}")
    
    # 如果是目录，显示内容
    if path_obj.is_dir():
        try:
            items = list(path_obj.iterdir())
            info.append(f"包含项目: {len(items)} 个")
            if items:
                # 显示前10个项目
                item_list = []
                for item in items[:10]:
                    item_type = "📁" if item.is_dir() else "📄"
                    item_list.append(f"  {item_type} {item.name}")
                info.append("内容预览:")
                info.extend(item_list)
                if len(items) > 10:
                    info.append(f"  ... 还有 {len(items) - 10} 个项目")
        except PermissionError:
            info.append("内容预览: 无权限访问")
    
    # 如果是文件，显示内容
    elif path_obj.is_file():
        try:
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if preview_full:
                    # 显示完整内容
                    info.append("文件内容:")
                    info.append(content)
                else:
                    # 只显示指定行数
                    lines = content.splitlines()
                    preview = lines[:preview_lines]
                    
                    if preview:
                        info.append(f"文件内容预览（前{preview_lines}行）:")
                        for line in preview:
                            info.append(f"  {line[:200]}")
                        if len(lines) > preview_lines:
                            info.append(f"  ... (还有 {len(lines) - preview_lines} 行未显示，共 {len(lines)} 行)")
                            info.append(f"提示: 如果需要完整内容，请使用 preview_full=True 参数")
        except (UnicodeDecodeError, PermissionError):
            info.append("文件内容预览: 二进制文件或无权限读取")
    
    # 显示工作目录信息
    if full_path.startswith(os.path.abspath(WORKDIR_ROOT)):
        rel_path = os.path.relpath(full_path, WORKDIR_ROOT)
        info.append(f"\n提示: 此路径在工作目录内 (相对于工作目录: {rel_path})")
    
    return "\n".join(info)


def check_multiple_paths(paths):
    """批量检测多个路径
    
    Args:
        paths: 路径列表
    
    Returns:
        所有路径检测结果的字符串
    """
    results = []
    for i, path in enumerate(paths, 1):
        results.append(f"=== 项目 {i}: {path} ===")
        results.append(check_path(path))
        results.append("")  # 空行分隔
    
    return "\n".join(results)


def find_files(directory, pattern="*", recursive=True):
    """在目录中查找匹配的文件
    
    Args:
        directory: 要搜索的目录
        pattern: 文件名模式（支持通配符，如 "*.txt", "test*"）
        recursive: 是否递归搜索子目录
    
    Returns:
        匹配的文件列表
    """
    # 标准化路径
    full_path = normalize_path(directory)
    
    # 检查权限
    allowed, _ = is_path_allowed(full_path)
    if not allowed:
        return f"错误：无权访问此路径 {full_path}"
    
    if not os.path.exists(full_path):
        return f"路径不存在: {full_path}"
    
    if not os.path.isdir(full_path):
        return f"不是目录: {full_path}"
    
    # 搜索文件
    path_obj = Path(full_path)
    if recursive:
        matches = list(path_obj.rglob(pattern))
    else:
        matches = list(path_obj.glob(pattern))
    
    if not matches:
        return f"未找到匹配 '{pattern}' 的文件"
    
    # 格式化结果
    results = [f"找到 {len(matches)} 个匹配 '{pattern}' 的文件:"]
    for match in matches[:20]:  # 最多显示20个
        rel_path = os.path.relpath(match, WORKDIR_ROOT)
        results.append(f"  📄 {rel_path}")
    
    if len(matches) > 20:
        results.append(f"  ... 还有 {len(matches) - 20} 个文件")
    
    return "\n".join(results)
