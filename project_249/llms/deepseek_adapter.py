from typing import Iterator, List, Dict, Any, Optional
import openai
from openai import APITimeoutError, APIError, RateLimitError, AuthenticationError
from ..config.settings import settings
from .base import BaseLLM, Message


class LLMError(Exception):
    """LLM调用错误基类"""
    pass


class LLMTimeoutError(LLMError):
    """LLM调用超时错误"""
    pass


class LLMAuthError(LLMError):
    """LLM认证错误"""
    pass


class LLMRateLimitError(LLMError):
    """LLM速率限制错误"""
    pass


class DeepSeekAdapter(BaseLLM):
    """
    DeepSeek LLM适配器
    
    支持错误处理、超时控制和降级策略。
    """
    
    def __init__(
        self,
        timeout: float = 60.0,
        max_retries: int = 3,
        default_temperature: float = 0.7,
        default_max_tokens: int = 1024,
    ):
        """
        初始化DeepSeek适配器。
        
        参数：
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            default_temperature: 默认温度参数
            default_max_tokens: 默认最大token数
        """
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.model = settings.DEEPSEEK_MODEL_NAME
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
    
    def _handle_error(self, error: Exception) -> None:
        """处理LLM调用错误"""
        if isinstance(error, APITimeoutError):
            raise LLMTimeoutError(f"LLM调用超时: {error}")
        elif isinstance(error, AuthenticationError):
            raise LLMAuthError(f"LLM认证失败，请检查API密钥: {error}")
        elif isinstance(error, RateLimitError):
            raise LLMRateLimitError(f"LLM速率限制，请稍后重试: {error}")
        elif isinstance(error, APIError):
            raise LLMError(f"LLM API错误: {error}")
        else:
            raise LLMError(f"LLM调用失败: {error}")
    
    def chat(
        self,
        messages,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        调用LLM进行对话。
        
        参数：
            messages: 消息列表
            max_tokens: 最大token数
            temperature: 温度参数
            
        返回：
            LLM响应内容
            
        异常：
            LLMTimeoutError: 请求超时
            LLMAuthError: 认证失败
            LLMRateLimitError: 速率限制
            LLMError: 其他LLM错误
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                extra_body={"thinking": {"type": "disabled"}}
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            self._handle_error(e)
    
    def chat_with_fallback(
        self,
        messages,
        fallback_response: str = "抱歉，服务暂时不可用，请稍后重试。",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        带降级策略的对话调用。
        
        当LLM调用失败时，返回预设的降级响应。
        
        参数：
            messages: 消息列表
            fallback_response: 降级响应内容
            max_tokens: 最大token数
            temperature: 温度参数
            
        返回：
            LLM响应内容或降级响应
        """
        try:
            return self.chat(messages, max_tokens, temperature)
        except (LLMTimeoutError, LLMError) as e:
            # 记录错误但返回降级响应
            import sys
            print(f"LLM调用失败，使用降级响应: {e}", file=sys.stderr)
            return fallback_response
    
    def chat_stream(
        self,
        messages,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Iterator[str]:
        """
        流式调用LLM进行对话。
        
        参数：
            messages: 消息列表
            max_tokens: 最大token数
            temperature: 温度参数
            
        Yields：
            响应内容片段
            
        异常：
            LLMTimeoutError: 请求超时
            LLMAuthError: 认证失败
            LLMRateLimitError: 速率限制
            LLMError: 其他LLM错误
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                stream=True,
                extra_body={"thinking": {"type": "disabled"}}
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e)
    
    def validate_connection(self) -> bool:
        """
        验证API连接是否正常。
        
        返回：
            连接是否正常
        """
        try:
            self.chat([{"role": "user", "content": "test"}], max_tokens=10)
            return True
        except Exception:
            return False
