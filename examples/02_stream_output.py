"""
示例 2: 流式输出

这个示例展示了如何使用真正的流式输出（不是逐字打印的假流式）。
"""

from project_249 import SimpleChatAgent
import sys


def main():
    print("=" * 50)
    print("示例 2: 流式输出")
    print("=" * 50)

    # 创建 Agent
    agent = SimpleChatAgent(
        memory_type="short_term",
        verbose=False,  # 静默模式，不显示内部日志
    )

    print("\n正在流式生成回答（你会看到文字逐字出现）...\n")

    # 使用流式输出
    query = "写一首关于春天的七言绝句，然后解释每句的意思"
    print(f"用户: {query}\n")
    print("Agent: ", end="", flush=True)

    for chunk in agent.chat_stream(query):
        print(chunk, end="", flush=True)

    print("\n")
    print("=" * 50)
    print("示例结束")
    print("=" * 50)


if __name__ == "__main__":
    main()
