"""
示例 5: 长期记忆

这个示例展示了如何使用长期记忆：
1. 存储重要信息
2. 持久化到磁盘
3. 语义检索相关记忆

注意：此示例需要有效的 API 密钥。
"""

from project_249 import LongTermMemory, Strategy
import tempfile
import shutil


def main():
    print("=" * 50)
    print("示例 5: 长期记忆")
    print("=" * 50)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建长期记忆
        print("\nStep 1: 创建长期记忆...")
        ltm = LongTermMemory(
            strategy=Strategy.MAP_REDUCE,
            store_path=temp_dir,
            single_max_token_num=500,
        )
        print(f"记忆总数: {ltm.count()}")

        # Step 2: 添加记忆
        print("\nStep 2: 添加记忆...")
        memories_to_add = [
            "用户叫小明，今年 25 岁",
            "用户喜欢的颜色是蓝色和绿色",
            "用户的生日是 1 月 1 日",
            "用户的职业是软件工程师",
            "用户喜欢吃火锅和烧烤",
            "用户最近在学习 AI Agent 开发",
        ]

        for mem in memories_to_add:
            ltm.add(mem)
            print(f"  已添加: {mem}")

        print(f"\n记忆总数: {ltm.count()}")

        # Step 3: 语义检索
        print("\nStep 3: 语义检索记忆...")

        test_queries = [
            "用户喜欢什么颜色？",
            "用户多大了？",
            "用户做什么工作？",
            "用户的生日是什么时候？",
        ]

        for query in test_queries:
            print(f"\n--- 查询: {query} ---")

            # 检索最相关的 2 条记忆
            memories = ltm.retrieval(query, k=2)
            print(f"检索到 {len(memories)} 条相关记忆:")
            for i, mem in enumerate(memories, 1):
                print(f"  {i}. {mem}")

            # 带相似度分数
            results = ltm.retrieval_with_scores(query, k=2)
            print(f"\n带相似度分数:")
            for i, (mem, score) in enumerate(results, 1):
                print(f"  {i}. [相似度 {score:.2f}] {mem}")

            # 格式化上下文（适合传给 LLM）
            context = ltm.format_for_context()
            if context:
                print(f"\n格式化后的上下文:\n{context}")

        # Step 4: 持久化验证
        print("\nStep 4: 验证持久化...")
        print(f"当前记忆数: {ltm.count()}")

        # 创建新的记忆实例（模拟重启程序）
        print("\n创建新的记忆实例（模拟重启程序）...")
        ltm2 = LongTermMemory(
            strategy=Strategy.MAP_REDUCE,
            store_path=temp_dir,
        )
        print(f"新实例的记忆数: {ltm2.count()}")

        # 新实例也能检索到之前的记忆
        print("\n新实例检索记忆:")
        memories = ltm2.retrieval("用户喜欢什么", k=2)
        for mem in memories:
            print(f"  - {mem}")

    finally:
        # 清理（实际使用时不要删除）
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 50)
    print("示例结束")
    print("=" * 50)


if __name__ == "__main__":
    main()
