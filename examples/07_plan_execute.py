"""
示例 7: Plan-Execute Agent - 规划执行模式

Plan-Execute 模式将复杂任务分解为：
1. Plan（规划）: 将大任务拆分为多个子任务
2. Execute（执行）: 按依赖关系顺序执行子任务
3. Report（报告）: 汇总所有子任务的结果

适合处理：多步骤操作、项目初始化、批量任务等。
"""

from project_249 import PlanExecuteAgent


def main():
    print("=" * 60)
    print("示例 7: Plan-Execute Agent - 规划执行模式")
    print("=" * 60)

    # 创建 Plan-Execute Agent
    # 参数说明：
    # - max_retries: 任务失败时的最大重试次数
    # - verbose: 显示详细的任务规划和执行过程
    agent = PlanExecuteAgent(
        memory_type="short_term",
        max_retries=2,
        verbose=True,
    )

    print("\nPlan-Execute Agent 创建成功！\n")

    # 测试 1: 简单任务规划
    print("-" * 40)
    print("测试 1: 创建项目目录结构")
    print("-" * 40)
    response = agent.chat(
        "请为我规划并创建一个 Python 项目的基础目录结构，"
        "包括 src/、tests/、docs/ 目录，以及一个 README.md 文件"
    )
    print(f"\n任务执行报告:\n{response}\n")

    # 测试 2: 多步骤信息获取
    print("-" * 40)
    print("测试 2: 获取时间信息")
    print("-" * 40)
    response = agent.chat("获取当前时间和日期，并告诉我距离周末还有几天")
    print(f"\n任务执行报告:\n{response}\n")

    print("=" * 60)
    print("示例结束 - Plan-Execute 模式的核心优势是：")
    print("1. 自动将复杂任务分解为可执行的子任务")
    print("2. 明确的任务依赖关系管理")
    print("3. 清晰的执行状态和结果报告")
    print("=" * 60)


if __name__ == "__main__":
    main()
