"""
示例 1: 最简单的对话

这个示例展示了如何创建一个基本的 Agent 并进行对话。

在运行此示例之前，请确保：
1. 已安装依赖: pip install -r requirements.txt
2. 已配置 API 密钥: 在 config/.env 中设置 DEEPSEEK_API_KEY
"""

from project_249 import SimpleChatAgent


def main():
    print("=" * 50)
    print("示例 1: 最简单的对话")
    print("=" * 50)

    # 创建 Agent
    # 参数说明：
    # - memory_type: "short_term" 短期记忆 或 "long_term" 长期记忆
    # - verbose: 是否显示日志（调试时设为 True，生产环境可设为 False）
    agent = SimpleChatAgent(
        memory_type="short_term",
        verbose=True,
    )

    print("\nAgent 创建成功！开始对话...\n")

    # 对话 1
    response = agent.chat("你好，请介绍一下你自己")
    print(f"用户: 你好，请介绍一下你自己")
    print(f"Agent: {response}\n")

    # 对话 2（Agent 会记得之前的对话历史）
    response = agent.chat("我叫小明，你能记住我的名字吗？")
    print(f"用户: 我叫小明，你能记住我的名字吗？")
    print(f"Agent: {response}\n")

    # 对话 3（测试记忆）
    response = agent.chat("我叫什么名字？")
    print(f"用户: 我叫什么名字？")
    print(f"Agent: {response}\n")

    print("=" * 50)
    print("示例结束")
    print("=" * 50)


if __name__ == "__main__":
    main()
