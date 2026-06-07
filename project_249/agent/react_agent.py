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
        """
        self.verbose = verbose
        self.max_iterations = max_iterations
        
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
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": "你是一个 ReAct 模式的智能助手。你会通过思考、行动、观察的循环来解决问题。"}
        ]
        
        self.logger.agent(f"ReAct Agent 初始化完成 (memory={memory_type}, max_iterations={max_iterations})")

    def _default_system_prompt(self) -> str:
        """默认的系统提示词"""
        return """你是一个 ReAct 模式的智能助手。

## 工作流程
对于每个用户问题，你需要通过以下循环来解决：

1. **Thought（思考）**：分析当前情况，明确问题所在，决定下一步行动
2. **Action（行动）**：选择一个工具并执行
3. **Observation（观察）**：获取工具执行结果，分析是否解决了问题

## 工具调用格式
当你需要使用工具时，必须按照以下格式：
<tool_call>工具名|{"参数名": "参数值"}</tool_call>

## 结束条件
当你认为问题已经解决时，直接给出最终答案。
不要继续调用工具。

## 示例
用户：北京今天天气怎么样？
Thought：我需要查询北京的天气，应该使用 weather_query 工具。
Action：weather_query
Observation：获取到天气信息
Final Answer：北京今天天气晴，温度 25℃，适合外出。
"""

    def _build_react_prompt(self, user_input: str, history: List[Dict]) -> str:
        """构建 ReAct 格式的提示词"""
        history_text = self._format_history(history)
        
        prompt = f"""
当前对话历史：
{history_text}

用户问题：{user_input}

请按照以下格式回答：
Thought：分析问题，决定下一步行动
Action：<tool_call>工具名|{{"参数名": "参数值"}}</tool_call> 或 "final_answer"

请开始：
"""
        return prompt

    def _format_history(self, history: List[Dict]) -> str:
        """格式化对话历史"""
        parts = []
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                continue
            elif role == "user":
                parts.append(f"用户：{content}")
            elif role == "assistant":
                parts.append(f"助手：{content}")
            elif role == "tool":
                parts.append(f"工具结果：{content}")
        return "\n".join(parts)

    def _process_single_action(self, user_input: str, history: List[Dict]) -> str:
        """处理单次 ReAct 循环"""
        prompt = self._build_react_prompt(user_input, history)
        
        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        return response

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
        
        history = list(self.memory.historys)
        
        for iteration in range(self.max_iterations):
            self.logger.agent(f"ReAct 迭代 {iteration + 1}/{self.max_iterations}")
            
            response = self._process_single_action(user_input, history)
            self.logger.tool(f"LLM 响应: {response[:200]}...")
            
            # 检查是否是最终答案
            if "final_answer" in response.lower() or "final answer" in response.lower():
                final_answer = self._extract_final_answer(response)
                self.memory.add({"role": "assistant", "content": final_answer})
                self.logger.agent(f"最终答案: {final_answer}")
                return final_answer
            
            # 检查是否需要调用工具
            if "<tool_call>" in response:
                tool_result = self._execute_tool_loop(response, history)
                history.extend(tool_result)
            else:
                # 没有工具调用，可能是直接回答
                self.memory.add({"role": "assistant", "content": response})
                return response
        
        # 达到最大迭代次数
        self.logger.warn(f"达到最大迭代次数 {self.max_iterations}，返回当前结果")
        return "抱歉，我无法在有限的迭代次数内完成这个问题。"

    def _execute_tool_loop(self, response: str, history: List[Dict]) -> List[Dict]:
        """执行工具调用循环"""
        tool_messages = []
        
        # 解析工具调用
        import re
        tool_pattern = r'<tool_call>([^|]+)\|({[^}]+})</tool_call>'
        matches = re.findall(tool_pattern, response)
        
        for tool_name, args_str in matches:
            self.logger.tool(f"调用工具: {tool_name}")
            
            # 构造一个模拟的消息对象
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
                        history.append(r)
                else:
                    self.logger.tool(f"工具结果: {str(results)[:100]}...")
                    tool_messages.append(results)
                    history.append(results)
        
        return tool_messages

    def _extract_final_answer(self, response: str) -> str:
        """从响应中提取最终答案"""
        import re
        
        # 尝试多种模式提取最终答案
        patterns = [
            r'[Ff]inal [Aa]nswer[：:]\s*(.+?)(?:\n|$)',
            r'[Ff]inal[：:]\s*(.+?)(?:\n|$)',
            r'答案[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1).strip()
        
        # 如果没有匹配到特定格式，返回整个响应
        return response.strip()

    def chat_stream(self, user_input: str) -> Iterator[str]:
        """流式输出版本"""
        response = self.chat(user_input)
        for char in response:
            yield char

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
