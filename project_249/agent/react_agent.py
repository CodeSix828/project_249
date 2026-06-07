from typing import Optional, Iterator, List, Dict, Any
from .base import BaseAgent
from ..llms.deepseek_adapter import DeepSeekAdapter
from ..llms.deepseek_function_call import DeepSeekCallTool
from ..memory.base import Strategy
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory
from ..tools.tools_list import tools
from ..tools.base import parse_function_call
from ..prompts.personas import get_persona
from ..utils.logger import Logger, LogHandler, LogCategory


class ReActAgent(BaseAgent):
    """
    ReAct 模式的 Agent（Reasoning + Acting）。
    
    ReAct 模式的核心流程：
    1. Thought（思考）：分析当前情况，决定下一步行动
    2. Action（行动）：选择并执行工具
    3. Observation（观察）：获取行动结果
    4. 循环直到得到最终答案
    
    这种模式让 Agent 能够：
    - 进行多步推理
    - 自主调用工具
    - 根据反馈调整策略
    - 处理复杂任务
    """

    def __init__(
        self,
        memory_type: str = "short_term",
        compare_type: Strategy = Strategy.SUMMARY,
        verbose: bool = True,
        log_handler: Optional[LogHandler] = None,
        enabled_logs: Optional[list[str]] = None,
        max_iterations: int = 10,
        stream_output: bool = True,
    ):
        """
        初始化 ReAct Agent。
        
        参数：
            memory_type: 记忆类型，"short_term" 或 "long_term"
            compare_type: 记忆策略
            verbose: 是否显示日志
            log_handler: 自定义日志处理器
            enabled_logs: 启用的日志类别
            max_iterations: 最大迭代次数，防止无限循环
            stream_output: 是否启用流式输出
        """
        self.verbose = verbose
        self.max_iterations = max_iterations
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
        
        persona = get_persona(persona_name="react")
        system_prompt_content = persona["system_prompt"] if persona else self._default_system_prompt()
        self.memory.historys = [
            {"role": "system", "content": system_prompt_content}
        ]
        
        self.logger.agent(f"ReAct Agent 初始化完成 (memory={memory_type}, max_iterations={max_iterations})")

    def _default_system_prompt(self) -> str:
        """默认的系统提示词"""
        return """你是一个 ReAct 模式的智能助手（Reasoning + Acting）。

## 核心工作流程
对于每个用户问题，你需要通过以下循环来解决：

1. **Thought（思考）**：分析当前情况，明确问题所在，决定下一步行动
2. **Action（行动）**：选择一个工具并执行
3. **Observation（观察）**：获取工具执行结果，分析是否解决了问题
4. **循环**：重复上述步骤，直到问题解决

## 可用工具
你可以使用以下工具：
- `weather_query`：查询指定城市的天气
- `square_calculate`：计算数值的平方
- `mkdir`：创建目录
- `write_to_file`：写入文件
- `check_path`：检查路径是否存在
- `find_files`：搜索文件

## 重要规则
- **不要编造信息**：所有信息必须来自工具，不能凭空编造
- **不要猜测工具结果**：必须实际调用工具获取结果
- **明确结束条件**：当你确认问题已解决时，直接给出答案

## 回复格式
请按照以下格式输出：
Thought：这里写下你的思考过程
Action：这里选择并调用工具

或者当任务完成时：
Thought：我已经获取到足够的信息，可以回答用户问题了。
Answer：这里给出最终答案
"""

    def _build_react_prompt(self, user_input: str) -> List[Dict]:
        """构建 ReAct 格式的消息列表"""
        prompt = f"""当前对话历史已在上下文中。

用户问题：{user_input}

请按照以下格式回答：
Thought：分析问题，决定下一步行动
Action：选择并调用工具

或者当任务完成时：
Thought：分析当前情况，确认问题解决
Answer：这里给出最终答案

请开始：
"""
        
        messages = list(self.memory.historys)
        messages.append({"role": "user", "content": prompt})
        
        return messages

    def _parse_and_execute_tools(self, response: str) -> List[Dict]:
        """解析工具调用并执行"""
        tool_messages = []
        
        import re
        tool_pattern = r'<tool_call>([^|]+)\|({[^}]+})</tool_call>'
        matches = re.findall(tool_pattern, response)
        
        if matches:
            for tool_name, args_str in matches:
                self.logger.tool(f"调用工具: {tool_name}")
                
                class ToolCallMessage:
                    def __init__(self, name, args):
                        self.tool_calls = [type('obj', (object,), {
                            'id': f'tool_{tool_name}',
                            'function': type('obj', (object,), {
                                'name': name,
                                'arguments': args
                            })
                        })()]
                
                msg = ToolCallMessage(tool_name, args_str)
                results = parse_function_call(msg)
                
                if results:
                    if isinstance(results, list):
                        for r in results:
                            self.logger.tool(f"工具结果: {str(r)[:100]}...")
                            tool_messages.append(r)
                    else:
                        self.logger.tool(f"工具结果: {str(results)[:100]}...")
                        tool_messages.append(results)
        else:
            # 尝试用 DeepSeekCallTool 进行工具选择
            self.logger.tool("尝试使用工具选择模型...")
            call_tool_response = self.llm_tool.call_llm(
                response, 
                tools, 
                self.memory.historys
            )
            
            if call_tool_response.tool_calls:
                self.logger.tool(f"工具选择模型决定使用工具: {call_tool_response.tool_calls}")
                results = parse_function_call(call_tool_response)
                if results:
                    tool_messages.extend(results if isinstance(results, list) else [results])
        
        return tool_messages

    def chat(self, user_input: str) -> str:
        """
        执行 ReAct 对话。
        
        通过多轮思考-行动-观察循环来解决问题。
        
        参数：
            user_input: 用户输入
            
        返回：
            最终答案
        """
        self.memory.add({"role": "user", "content": user_input})
        self.logger.agent(f"用户输入: {user_input}")
        
        final_answer = None
        
        for iteration in range(self.max_iterations):
            self.logger.agent(f"ReAct 迭代 {iteration + 1}/{self.max_iterations}")
            
            messages = self._build_react_prompt(user_input)
            
            self.logger.llm("调用 LLM 进行思考...")
            response = self.llm.chat(messages)
            self.logger.tool(f"LLM 响应: {response[:200]}...")
            
            # 先添加 Assistant 的响应到记忆
            self.memory.add({"role": "assistant", "content": response})
            
            # 检查是否是最终答案
            if "Answer：" in response or "Answer:" in response or "Final Answer：" in response or "Final Answer:" in response:
                final_answer = self._extract_final_answer(response)
                self.logger.agent(f"最终答案: {final_answer}")
                return final_answer
            
            # 检查是否需要调用工具
            if "<tool_call>" in response or "Action：" in response or "Action:" in response:
                tool_messages = self._parse_and_execute_tools(response)
                if tool_messages:
                    self.memory.historys.extend(tool_messages)
                    self.logger.agent("工具执行完成，继续循环...")
                else:
                    self.logger.agent("没有工具调用，尝试直接回答...")
                    final_answer = self._extract_final_answer(response)
                    if final_answer:
                        return final_answer
                    return response
            else:
                # 没有工具调用，可能是直接回答
                self.logger.agent("没有工具调用，尝试提取答案...")
                final_answer = self._extract_final_answer(response)
                if final_answer:
                    return final_answer
                return response
        
        # 达到最大迭代次数
        self.logger.warn(f"达到最大迭代次数 {self.max_iterations}，返回当前结果")
        return "抱歉，我无法在有限的迭代次数内完成这个问题。"

    def _extract_final_answer(self, response: str) -> str:
        """从响应中提取最终答案"""
        import re
        
        patterns = [
            r'[Ff]inal [Aa]nswer[：:]\s*(.+?)(?:\n|$)',
            r'[Ff]inal[：:]\s*(.+?)(?:\n|$)',
            r'[Aa]nswer[：:]\s*(.+?)(?:\n|$)',
            r'答案[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1).strip()
        
        return response.strip()

    def chat_stream(self, user_input: str) -> Iterator[str]:
        """流式输出版本"""
        self.memory.add({"role": "user", "content": user_input})
        self.logger.agent(f"用户输入: {user_input}")
        
        full_response = []
        final_answer = None
        
        for iteration in range(self.max_iterations):
            self.logger.agent(f"ReAct 迭代 {iteration + 1}/{self.max_iterations}")
            
            messages = self._build_react_prompt(user_input)
            
            self.logger.llm("调用 LLM 进行思考（流式）...")
            
            current_iteration_response = []
            for chunk in self.llm.chat_stream(messages):
                current_iteration_response.append(chunk)
                yield chunk
            
            response = ''.join(current_iteration_response)
            full_response.append(response)
            
            self.memory.add({"role": "assistant", "content": response})
            
            if "Answer：" in response or "Answer:" in response or "Final Answer：" in response or "Final Answer:" in response:
                final_answer = self._extract_final_answer(response)
                self.logger.agent(f"最终答案: {final_answer}")
                return
            
            if "<tool_call>" in response or "Action：" in response or "Action:" in response:
                tool_messages = self._parse_and_execute_tools(response)
                if tool_messages:
                    self.memory.historys.extend(tool_messages)
                    self.logger.agent("工具执行完成，继续循环...")
                else:
                    final_answer = self._extract_final_answer(response)
                    if final_answer:
                        return
            else:
                final_answer = self._extract_final_answer(response)
                if final_answer:
                    return
                return
        
        self.logger.warn(f"达到最大迭代次数 {self.max_iterations}")
        yield "抱歉，我无法在有限的迭代次数内完成这个问题。"

    def set_verbose(self, verbose: bool):
        self.verbose = verbose
        self.logger.set_verbose(verbose)

    def set_log_handler(self, handler: LogHandler):
        self.logger.set_handler(handler)

    def set_enabled_logs(self, categories: list[str] | None):
        self.logger.set_enabled_categories(categories)

    def enable_log(self, category: str):
        self.logger.enable_category(category)

    def disable_log(self, category: str):
        self.logger.disable_category(category)

    def get_enabled_logs(self) -> list[str]:
        return [c.value for c in self.logger.get_enabled_categories()]

    def set_stream_output(self, enabled: bool):
        self.stream_output = enabled