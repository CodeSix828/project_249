"""
DeepSeek API 工具选择模块

负责决定是否需要调用工具以及调用哪个工具。
"""

import openai
from openai import APITimeoutError, APIError, RateLimitError, AuthenticationError
from ..config.settings import settings


class ToolCallError(Exception):
    """工具调用错误基类"""
    pass


class ToolCallTimeoutError(ToolCallError):
    """工具调用超时错误"""
    pass


class ToolCallAuthError(ToolCallError):
    """工具调用认证错误"""
    pass


class ToolCallRateLimitError(ToolCallError):
    """工具调用速率限制错误"""
    pass


class DeepSeekCallTool:
    """
    DeepSeek 工具选择模块
    
    负责根据用户输入和上下文，决定是否调用工具以及调用哪个工具。
    支持错误处理和超时控制。
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """
        初始化工具选择模块。
        
        参数：
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.model = settings.DEEPSEEK_MODEL_NAME
    
    def _handle_error(self, error: Exception) -> None:
        """处理工具调用错误"""
        if isinstance(error, APITimeoutError):
            raise ToolCallTimeoutError(f"工具选择超时: {error}")
        elif isinstance(error, AuthenticationError):
            raise ToolCallAuthError(f"工具选择认证失败: {error}")
        elif isinstance(error, RateLimitError):
            raise ToolCallRateLimitError(f"工具选择速率限制: {error}")
        elif isinstance(error, APIError):
            raise ToolCallError(f"工具选择API错误: {error}")
        else:
            raise ToolCallError(f"工具选择失败: {error}")
    
    def call_llm(
        self,
        message,
        tools,
        memory_context,
    ):
        """
        调用LLM进行工具选择。
        
        参数：
            message: 用户消息
            tools: 可用工具列表
            memory_context: 记忆上下文
            
        返回：
            ChatCompletionMessage 对象，包含 content 和 tool_calls
            
        异常：
            ToolCallTimeoutError: 请求超时
            ToolCallAuthError: 认证失败
            ToolCallRateLimitError: 速率限制
            ToolCallError: 其他错误
        """
        system_prompt = f"""你是主对话模型的内部工具选择模块。
当前对话上下文（仅供参考，不要写入你的回复）：
{memory_context if memory_context else "无历史对话"}

你需要：
1. 只输出工具调用，不要有任何解释
2. 输出格式必须是：<tool_call>工具名|参数JSON</tool_call>
3. 如果不需要工具：<no_tool></no_tool>
4. 不要输出任何其他内容"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                extra_body={"thinking": {"type": "disabled"}}
            )
            return response.choices[0].message
        except Exception as e:
            self._handle_error(e)
    
    def call_llm_with_fallback(
        self,
        message,
        tools,
        memory_context,
    ):
        """
        带降级策略的工具选择调用。
        
        当工具选择失败时，返回不调用任何工具的响应。
        
        参数：
            message: 用户消息
            tools: 可用工具列表
            memory_context: 记忆上下文
            
        返回：
            ChatCompletionMessage 对象
        """
        try:
            return self.call_llm(message, tools, memory_context)
        except ToolCallError as e:
            import sys
            print(f"工具选择失败，返回空选择: {e}", file=sys.stderr)
            # 返回一个没有tool_calls的消息
            class NoToolResponse:
                content = "<no_tool></no_tool>"
                tool_calls = None
            return NoToolResponse()
    
    def validate_connection(self) -> bool:
        """
        验证API连接是否正常。
        
        返回：
            连接是否正常
        """
        try:
            self.call_llm("test", [], None)
            return True
        except Exception:
            return False
