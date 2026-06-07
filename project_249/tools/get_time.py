from datetime import datetime

def get_current_time():
    """获取当前系统时间和日期
    
    Returns:
        包含当前时间信息的字符串
    """
    now = datetime.now()
    
    # 格式化时间
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y年%m月%d日")
    week_day = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()]
    
    info = []
    info.append(f"当前时间: {time_str}")
    info.append(f"日期: {date_str}")
    info.append(f"星期: {week_day}")
    info.append(f"时间戳: {int(now.timestamp())}")
    
    return "\n".join(info)


def get_current_date():
    """获取当前日期（简化版）
    
    Returns:
        包含当前日期的字符串
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    return f"当前日期: {date_str}"
