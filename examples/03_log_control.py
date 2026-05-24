"""
示例 3: 日志控制

这个示例展示了如何控制日志输出，适合作为第三方库使用时。
"""

from project_249 import SimpleChatAgent
from project_249.utils import LogCategory


def my_custom_log_handler(level, message, category):
    """
    自定义日志处理器

    当你把这个项目作为第三方库嵌入到你的应用中时，
    可以使用这个方法将日志转发到你应用的日志系统。
    """
    if category:
        print(f"[自定义日志 - {category.value}] {message}")
    else:
        print(f"[自定义日志] {message}")


def main():
    print("=" * 50)
    print("示例 3: 日志控制")
    print("=" * 50)

    # 方式 1: 静默模式（完全不输出日志）
    print("\n--- 方式 1: 静默模式 ---")
    agent1 = SimpleChatAgent(
        memory_type="short_term",
        verbose=False,  # 完全静默
    )
    response = agent1.chat("你好")
    print(f"回答: {response}")

    # 方式 2: 只启用特定日志分类
    print("\n--- 方式 2: 只启用特定日志分类 ---")
    agent2 = SimpleChatAgent(
        memory_type="short_term",
        verbose=True,
        enabled_logs=["agent", "error"],  # 只显示 agent 和 error 类别的日志
    )
    response = agent2.chat("介绍一下你自己")
    print(f"回答: {response}")

    # 方式 3: 自定义日志处理器
    print("\n--- 方式 3: 自定义日志处理器 ---")
    agent3 = SimpleChatAgent(
        memory_type="short_term",
        verbose=True,
        log_handler=my_custom_log_handler,
        enabled_logs=["agent"],
    )
    response = agent3.chat("你好")
    print(f"回答: {response}")

    # 方式 4: 动态修改日志配置
    print("\n--- 方式 4: 动态修改日志配置 ---")
    agent4 = SimpleChatAgent(
        memory_type="short_term",
        verbose=False,  # 初始静默
    )

    print("初始状态: 静默模式")
    response = agent4.chat("你好")

    print("\n临时启用 LLM 日志用于调试...")
    agent4.set_verbose(True)
    agent4.set_enabled_logs(["llm"])
    response = agent4.chat("你好")

    print("\n调试完成，恢复静默模式...")
    agent4.set_verbose(False)

    print("\n" + "=" * 50)
    print("示例结束")
    print("=" * 50)


if __name__ == "__main__":
    main()
