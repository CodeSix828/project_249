"""
示例 6: ReAct Agent - 思考-行动-观察循环

ReAct（Reasoning + Acting）模式让Agent能够：
1. 分析问题（Thought）
2. 决定使用什么工具（Action）
3. 观察工具结果（Observation）
4. 循环直到得到答案

这种模式特别适合需要多步推理或查找实时信息的问题。
"""

from project_249 import ReActAgent


def main():
    print("=" * 60)
    print("示例 6: ReAct Agent - 思考-行动-观察循环")
    print("=" * 60)

    # 创建 ReAct Agent
    # 参数说明：
    # - max_iterations: 最大迭代次数，防止无限循环
    # - memory_type: 记忆类型
    # - verbose: 显示详细日志，可看到思考过程
    agent = ReActAgent(
        memory_type="short_term",
        max_iterations=5,
        verbose=True,
    )

    print("\nReAct Agent 创建成功！\n")

    # 测试 1: 简单问题（不需要工具）
    print("-" * 40)
    print("测试 1: 简单问答")
    print("-" * 40)
    response = agent.chat("什么是 ReAct 模式？请用一句话解释。")
    print(f"\n答案: {response}\n")

    # 测试 2: 需要工具的问题
    print("-" * 40)
    print("测试 2: 获取当前时间（使用工具）")
    print("-" * 40)
    response = agent.chat("现在几点钟？今天是星期几？")
    print(f"\n答案: {response}\n")

    # 测试 3: 简单计算
    print("-" * 40)
    print("测试 3: 数值计算（使用工具）")
    print("-" * 40)
    response = agent.chat("12345 的平方是多少？")
    print(f"\n答案: {response}\n")

    print("=" * 60)
    print("示例结束 - ReAct 模式的核心优势是：")
    print("1. 可以自主决定是否使用工具")
    print("2. 每一步都有明确的思考过程")
    print("3. 可以处理复杂的多步任务")
    print("=" * 60)


if __name__ == "__main__":
    main()
