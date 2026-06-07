from typing import Optional, Iterator, List
from ..llms.deepseek_adapter import DeepSeekAdapter
from ..llms.deepseek_function_call import DeepSeekCallTool
from ..memory.base import Strategy
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory
from ..tools.tools_list import tools
from ..tools.base import parse_function_call
from ..prompts.personas import get_persona
from ..utils.logger import Logger, LogHandler, LogCategory
from .base import BaseAgent


class SimpleChatAgent(BaseAgent):
    def __init__(
        self,
        memory_type: str = "short_term",
        compare_type: Strategy = Strategy.SUMMARY,
        verbose: bool = True,
        log_handler: Optional[LogHandler] = None,
        enabled_logs: Optional[list[str]] = None,
        stream_output: bool = True,
    ):
        self.verbose = verbose
        self.stream_output = stream_output
        
        enabled_categories = None
        if enabled_logs is not None:
            enabled_categories = enabled_logs
        
        self.logger = Logger(
            verbose=verbose,
            enabled_categories=enabled_categories,
            handler=log_handler,
        )
        
        if memory_type == "short_term":
            self.memory = ShortTermMemory(compare_type)
        elif memory_type == "long_term":
            self.memory = LongTermMemory(compare_type)
        
        self.llm = DeepSeekAdapter()
        self.llm_tool = DeepSeekCallTool()
        
        persona = get_persona(persona_name="default")
        system_prompt_content = persona["system_prompt"]
        self.memory.historys = [
            {"role": "system", "content": f"{system_prompt_content}"},
            {"role": "user", "content": "用户：CodeSix828,登入"}
        ]
        
        self.logger.agent(f"初始化完成 (memory={memory_type})")

    def _log_tool_result(self, tool_name: str, args: dict, result: dict):
        if "error" in result:
            self.logger.tool(f"调用 {tool_name} 失败: {result}")
        else:
            result_preview = str(result)[:100]
            if len(str(result)) > 100:
                result_preview += "..."
            self.logger.tool(f"调用 {tool_name}({args}) -> {result_preview}")

    def _process_tools(self, user_input: str):
        call_tool_response = self.llm_tool.call_llm(user_input, tools, self.memory.historys)
        
        if call_tool_response.tool_calls:
            self.logger.tool(f"选择使用工具: {call_tool_response.content}")
            self.memory.add({
                "role": "assistant",
                "content": f"内部工具选择模型 {call_tool_response.content}",
                "tool_calls": call_tool_response.tool_calls
            })
        else:
            self.logger.tool("未选择任何工具")
            self.memory.add({
                "role": "assistant",
                "content": f"内部工具选择模型 {call_tool_response.content}"
            })
        
        tool_messages = parse_function_call(call_tool_response)
        if tool_messages:
            self.logger.tool(f"工具执行结果: {tool_messages}")
            self.memory.historys.extend(tool_messages)

    def chat(self, user_input: str) -> str:
        self.memory.add({"role": "user", "content": user_input})
        self.logger.agent(f"用户输入: {user_input}")
        
        self._process_tools(user_input)
        
        self.logger.llm("调用主对话模型...")
        response = self.llm.chat(self.memory.historys)
        self.memory.add({"role": "assistant", "content": f"主对话模型：{response}"})
        
        return response

    def chat_stream(self, user_input: str) -> Iterator[str]:
        self.memory.add({"role": "user", "content": user_input})
        self.logger.agent(f"用户输入: {user_input}")
        
        self._process_tools(user_input)
        
        self.logger.llm("调用主对话模型（流式）...")
        full_response = []
        for chunk in self.llm.chat_stream(self.memory.historys):
            full_response.append(chunk)
            yield chunk
        
        complete_text = ''.join(full_response)
        self.memory.add({"role": "assistant", "content": f"主对话模型：{complete_text}"})

    def set_verbose(self, verbose: bool):
        self.verbose = verbose
        self.logger.set_verbose(verbose)

    def set_log_handler(self, handler: LogHandler):
        self.logger.set_handler(handler)

    def set_stream_output(self, enabled: bool):
        self.stream_output = enabled

    def set_enabled_logs(self, categories: list[str] | None):
        self.logger.set_enabled_categories(categories)

    def enable_log(self, category: str):
        self.logger.enable_category(category)

    def disable_log(self, category: str):
        self.logger.disable_category(category)

    def get_enabled_logs(self) -> list[str]:
        return [c.value for c in self.logger.get_enabled_categories()]
