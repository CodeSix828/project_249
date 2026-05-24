from typing import Iterator, List, Dict, Any
import openai
from ..config.settings import settings
from .base import BaseLLM, Message


class DeepSeekAdapter(BaseLLM):
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        self.model = settings.DEEPSEEK_MODEL_NAME

    def chat(
        self,
        messages,
        max_tokens=1024,
        temperature=0.7,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body={"thinking": {"type": "disabled"}}
        )
        return response.choices[0].message.content

    def chat_stream(
        self,
        messages,
        max_tokens=1024,
        temperature=0.7,
    ) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            extra_body={"thinking": {"type": "disabled"}}
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
