"""
示例 8: 错误处理和降级策略

展示框架的健壮性：
1. LLM 调用超时处理
2. API 认证失败处理
3. 网络异常时的降级策略
4. 工具调用失败的优雅恢复

作为第三方库使用时，了解这些异常处理机制非常重要。
"""

from project_249 import SimpleChatAgent
from project_249.llms.deepseek_adapter import (
    DeepSeekAdapter,
    LLMError,
    LLMTimeoutError,
    LLMAuthError,
    LLMRateLimitError,
)


def demo_llm_error_handling():
    """演示 LLM 的错误处理"""
    print("=" * 60)
    print("1. LLM 错误处理机制")
    print("=" * 60)

    llm = DeepSeekAdapter()

    # 验证连接
    print("\n正在验证 API 连接...")
    if llm.validate_connection():
        print("✅ API 连接正常")
    else:
        print("⚠️  API 连接不可用（可能是网络问题或密钥未配置）")

    # 降级策略演示
    print("\n使用 chat_with_fallback() 降级:")
    print("当 LLM 调用失败时，会返回预设的降级响应而不是抛出异常。")
    response = llm.chat_with_fallback(
        [{"role": "user", "content": "你好"}],
        fallback_response="抱歉，服务暂时不可用，请稍后重试。"
    )
    print(f"结果: {response}\n")


def demo_agent_safe_usage():
    """演示 Agent 的安全使用模式"""
    print("=" * 60)
    print("2. Agent 的推荐使用模式")
    print("=" * 60)

    try:
        agent = SimpleChatAgent(
            memory_type="short_term",
            verbose=True,
        )
        print("\n✅ Agent 初始化成功")

        response = agent.chat("请用一句话介绍你自己。")
        print(f"回复: {response}\n")

    except LLMAuthError as e:
        print(f"❌ 认证失败，请检查 API 密钥配置: {e}")
    except LLMTimeoutError as e:
        print(f"⏱️  请求超时，请检查网络: {e}")
    except LLMRateLimitError as e:
        print(f"🔒 速率限制，请稍后重试: {e}")
    except LLMError as e:
        print(f"❌ LLM 调用错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


def main():
    print("\n" + "=" * 60)
    print("示例 8: 错误处理和降级策略")
    print("=" * 60)

    demo_llm_error_handling()
    demo_agent_safe_usage()

    print("\n" + "=" * 60)
    print("关键要点:")
    print("1. 使用 try-except 捕获具体的异常类型")
    print("2. 使用 chat_with_fallback() 确保服务可用性")
    print("3. 使用 validate_connection() 验证配置")
    print("=" * 60)


if __name__ == "__main__":
    main()
