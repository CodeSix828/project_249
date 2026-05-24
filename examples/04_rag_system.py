"""
示例 4: RAG 系统（检索增强生成）

这个示例展示了如何使用 RAG 系统：
1. 将文档分块
2. 存储到向量数据库
3. 检索相关文档
4. 基于检索结果生成回答

注意：此示例需要有效的 API 密钥，因为需要 Embedding 和 LLM 调用。
"""

from project_249 import SentenceTextSplitter, Database, create_rag_chain
import tempfile
import shutil


def main():
    print("=" * 60)
    print("示例 4: RAG 系统（检索增强生成）")
    print("=" * 60)

    # Step 1: 准备知识库
    print("\nStep 1: 准备知识库...")
    knowledge = """
    AI Agent 实验室是一个研究 AI Agent 的开源项目。

    这个项目的主要功能包括：
    1. RAG 检索增强生成 - 让 AI 能够引用外部知识回答问题
    2. 长短期记忆 - 同时支持会话记忆和持久化存储
    3. 工具调用 - Agent 可以自主调用预设工具完成任务
    4. 流式输出 - 支持真正的 SSE 流式传输
    5. 日志系统 - 六大分类，支持过滤和自定义回调

    项目使用 DeepSeek 作为默认的大语言模型。
    推荐使用的模型是 deepseek-v4-flash。

    这个项目既可以作为第三方库嵌入到其他应用中，
    也可以作为独立的软件运行。
    """
    print(f"知识库内容: {knowledge[:200]}...")

    # Step 2: 文档分块
    print("\nStep 2: 将文档分块...")
    splitter = SentenceTextSplitter(
        chunk_size=200,  # 每个块最大 200 字符
        chunk_overlap=20,  # 块之间重叠 20 字符
    )
    chunks = splitter.split_text(knowledge)
    print(f"分块数量: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"  块 {i}: {chunk[:50]}...")

    # Step 3: 创建数据库并存储
    print("\nStep 3: 创建向量数据库并存储...")
    # 使用临时目录，示例结束后自动清理
    temp_dir = tempfile.mkdtemp()
    try:
        db = Database(store_path=temp_dir)
        db.add_documents(chunks)  # 批量添加（高效）
        print(f"数据库中的文档数量: {db.count()}")

        # Step 4: 创建 RAG 链
        print("\nStep 4: 创建 RAG 链...")
        chain = create_rag_chain(
            database=db,
            k=2,  # 检索最相关的 2 个文档
            similarity_threshold=0.0,  # 相似度阈值（0.0 表示不过滤）
        )
        print("RAG 链创建成功！")

        # Step 5: 使用 RAG 链查询
        print("\nStep 5: 使用 RAG 链查询...")

        questions = [
            "这个项目有哪些主要功能？",
            "这个项目使用什么大语言模型？",
            "这个项目可以作为第三方库使用吗？",
        ]

        for question in questions:
            print(f"\n--- 问题: {question} ---")

            # 方式 1: 普通查询
            answer = chain.invoke(question)
            print(f"回答: {answer}")

            # 方式 2: 获取回答和使用的上下文（便于调试）
            result = chain.invoke_with_context(question)
            print("\n使用的上下文:")
            for i, (doc, score) in enumerate(result["contexts"], 1):
                print(f"  [{i}] 相似度 {score:.2f}: {doc[:80]}...")

        # 方式 3: 流式输出
        print("\n--- 流式输出示例 ---")
        print("问题: 详细介绍一下 RAG 功能")
        print("回答: ", end="", flush=True)
        for chunk in chain.invoke_stream("详细介绍一下 RAG 功能"):
            print(chunk, end="", flush=True)
        print()

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("示例结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
