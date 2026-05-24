#DeepSeek API处理工具选择
# llms/deepseek_adapter.py
import openai
from ..config.settings import settings

class DeepSeekCallTool:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
            
        )
        self.model = settings.DEEPSEEK_MODEL_NAME
    
    def call_llm(self, message, tools, memory_context):
        messages = [{"role": "system", "content":f'''你是主对话模型的内部工具选择模块。
                                        当前对话上下文（仅供参考，不要写入你的回复）：
                                        {memory_context if memory_context else "无历史对话"}
                                        你需要：
                                        1. 只输出工具调用，不要有任何解释
                                        2. 输出格式必须是：<tool_call>工具名|参数JSON</tool_call>
                                        3. 如果不需要工具：<no_tool></no_tool>
                                        4. 不要输出任何其他内容'''},
                    {"role": "user", "content": message}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",              #由大模型决定使用什么工具
            extra_body={"thinking": {"type": "disabled"}})  # 禁用思考模式   神奇bug勿动
        
        return response.choices[0].message     #message类下有content和tool_calls两个变量