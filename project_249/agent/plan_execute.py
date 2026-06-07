from typing import Optional, Iterator, List, Dict, Any, Callable
from enum import Enum
from .base import BaseAgent
from ..llms.deepseek_adapter import DeepSeekAdapter
from ..memory.base import Strategy
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory
from ..prompts.personas import get_persona
from ..utils.logger import Logger, LogHandler, LogCategory


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"       # 待执行
    RUNNING = "running"       # 执行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    SKIPPED = "skipped"       # 跳过


class Task:
    """任务类"""
    def __init__(
        self,
        task_id: str,
        description: str,
        status: TaskStatus = TaskStatus.PENDING,
        result: Any = None,
        error: str = None,
        dependencies: List[str] = None,
    ):
        self.task_id = task_id
        self.description = description
        self.status = status
        self.result = result
        self.error = error
        self.dependencies = dependencies or []
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
        }


class PlanExecuteAgent(BaseAgent):
    """
    Plan-Execute 模式的 Agent（规划-执行）。
    
    Plan-Execute 模式的核心流程：
    1. **Plan（规划）**：将复杂任务分解为多个子任务
    2. **Execute（执行）**：按依赖顺序执行子任务
    3. **Monitor（监控）**：监控执行状态，处理异常
    
    这种模式让 Agent 能够：
    - 处理复杂的多步骤任务
    - 明确任务依赖关系
    - 追踪任务执行状态
    - 处理任务执行失败
    """

    def __init__(
        self,
        memory_type: str = "short_term",
        compare_type: Strategy = Strategy.SUMMARY,
        verbose: bool = True,
        log_handler: Optional[LogHandler] = None,
        enabled_logs: Optional[list[str]] = None,
        max_retries: int = 3,
    ):
        """
        初始化 Plan-Execute Agent。
        
        参数：
            memory_type: 记忆类型，"short_term" 或 "long_term"
            compare_type: 记忆策略
            verbose: 是否显示日志
            log_handler: 自定义日志处理器
            enabled_logs: 启用的日志类别
            max_retries: 任务失败最大重试次数
        """
        self.verbose = verbose
        self.max_retries = max_retries
        self.tasks: List[Task] = []
        
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
        
        persona = get_persona(persona_name="planner")
        system_prompt_content = persona["system_prompt"] if persona else self._default_planner_prompt()
        self.memory.historys = [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": "你是一个任务规划专家，负责将复杂任务分解为可执行的子任务。"}
        ]
        
        self.logger.agent(f"Plan-Execute Agent 初始化完成 (memory={memory_type}, max_retries={max_retries})")

    def _default_planner_prompt(self) -> str:
        """默认的规划器系统提示词"""
        return """你是一个任务规划专家。

## 你的职责
将复杂用户请求分解为多个可执行的子任务，并确定任务之间的依赖关系。

## 输出格式
请以 JSON 格式输出任务规划：
{
    "tasks": [
        {
            "task_id": "task_1",
            "description": "任务描述",
            "dependencies": []  // 依赖的任务ID列表
        }
    ]
}

## 注意事项
1. 任务描述要清晰、具体、可执行
2. 明确任务之间的依赖关系
3. 尽可能并行化独立任务
4. 考虑任务的执行顺序"""

    def _default_executor_prompt(self) -> str:
        """默认的执行器系统提示词"""
        return """你是一个任务执行专家。

## 你的职责
根据任务描述，执行具体的操作并返回结果。

## 输出格式
直接返回执行结果即可。如果执行失败，返回错误信息。"""

    def _plan(self, user_input: str) -> List[Task]:
        """
        将用户输入分解为任务计划。
        
        参数：
            user_input: 用户输入
            
        返回：
            任务列表
        """
        self.logger.agent("开始规划任务...")
        
        prompt = f"""请将以下用户请求分解为具体的子任务：

用户请求：{user_input}

请以 JSON 格式输出任务规划，确保任务可以独立执行。"""
        
        response = self.llm.chat([
            {"role": "system", "content": self._default_planner_prompt()},
            {"role": "user", "content": prompt}
        ])
        
        self.logger.tool(f"规划响应: {response[:200]}...")
        
        tasks = self._parse_plan_response(response)
        
        for task in tasks:
            self.logger.agent(f"  - {task.task_id}: {task.description} (依赖: {task.dependencies})")
        
        return tasks

    def _parse_plan_response(self, response: str) -> List[Task]:
        """解析规划响应"""
        import re
        import json
        
        # 尝试提取 JSON
        json_pattern = r'\{[\s\S]*"tasks"[\s\S]*\}'
        match = re.search(json_pattern, response)
        
        if not match:
            # 尝试更宽松的匹配
            json_pattern = r'\[.*\]'
            match = re.search(json_pattern, response)
        
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict) and "tasks" in data:
                    tasks_data = data["tasks"]
                elif isinstance(data, list):
                    tasks_data = data
                else:
                    raise ValueError("Invalid format")
                
                tasks = []
                for i, task_data in enumerate(tasks_data):
                    if isinstance(task_data, dict):
                        task = Task(
                            task_id=task_data.get("task_id", f"task_{i}"),
                            description=task_data.get("description", ""),
                            dependencies=task_data.get("dependencies", []),
                        )
                        tasks.append(task)
                return tasks
            except Exception as e:
                self.logger.warn(f"解析规划响应失败: {e}")
        
        # 如果无法解析，返回单个任务
        self.logger.warn("无法解析任务规划，创建单个任务")
        return [Task(task_id="task_0", description=response, dependencies=[])]

    def _execute_task(self, task: Task) -> Any:
        """
        执行单个任务。
        
        参数：
            task: 任务对象
            
        返回：
            执行结果
        """
        self.logger.agent(f"执行任务 {task.task_id}: {task.description}")
        task.status = TaskStatus.RUNNING
        
        # 获取前置任务的结果作为上下文
        context = self._get_task_context(task)
        
        prompt = f"""任务：{task.description}

{context}

请执行这个任务并返回结果。"""
        
        try:
            result = self.llm.chat([
                {"role": "system", "content": self._default_executor_prompt()},
                {"role": "user", "content": prompt}
            ])
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.logger.agent(f"任务 {task.task_id} 完成")
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"任务 {task.task_id} 失败: {e}")
            return None

    def _get_task_context(self, task: Task) -> str:
        """获取任务的前置上下文"""
        if not task.dependencies:
            return ""
        
        context_parts = []
        for dep_id in task.dependencies:
            for t in self.tasks:
                if t.task_id == dep_id:
                    if t.status == TaskStatus.COMPLETED:
                        context_parts.append(f"[{dep_id}] {t.description}\n结果: {t.result}")
                    elif t.status == TaskStatus.FAILED:
                        context_parts.append(f"[{dep_id}] 已失败: {t.error}")
        
        if context_parts:
            return "前置任务结果：\n" + "\n\n".join(context_parts) + "\n\n"
        return ""

    def _can_execute(self, task: Task) -> bool:
        """检查任务是否可以执行（依赖是否满足）"""
        if task.status != TaskStatus.PENDING:
            return False
        
        for dep_id in task.dependencies:
            for t in self.tasks:
                if t.task_id == dep_id:
                    if t.status != TaskStatus.COMPLETED:
                        return False
        
        return True

    def _execute_plan(self) -> List[Task]:
        """
        执行任务计划。
        
        按依赖顺序执行所有任务。
        
        返回：
            执行完成的任务列表
        """
        self.logger.agent("开始执行计划...")
        
        completed_count = 0
        max_iterations = len(self.tasks) * 2  # 防止无限循环
        
        iteration = 0
        while completed_count < len(self.tasks) and iteration < max_iterations:
            iteration += 1
            
            for task in self.tasks:
                if self._can_execute(task):
                    self._execute_task(task)
            
            completed_count = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        
        return self.tasks

    def chat(self, user_input: str) -> str:
        """
        执行 Plan-Execute 对话。
        
        将用户输入分解为任务计划，然后按顺序执行。
        
        参数：
            user_input: 用户输入
            
        返回：
            最终执行结果
        """
        self.memory.add({"role": "user", "content": user_input})
        self.logger.agent(f"用户输入: {user_input}")
        
        # 规划阶段
        self.tasks = self._plan(user_input)
        
        # 执行阶段
        self._execute_plan()
        
        # 生成最终报告
        report = self._generate_execution_report()
        
        self.memory.add({"role": "assistant", "content": report})
        
        return report

    def _generate_execution_report(self) -> str:
        """生成执行报告"""
        report_parts = ["## 任务执行报告\n"]
        
        for task in self.tasks:
            status_icon = {
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.PENDING: "⏳",
                TaskStatus.SKIPPED: "⏭️",
            }.get(task.status, "❓")
            
            report_parts.append(f"{status_icon} **{task.task_id}**: {task.description}")
            
            if task.status == TaskStatus.COMPLETED:
                report_parts.append(f"   结果: {task.result}")
            elif task.status == TaskStatus.FAILED:
                report_parts.append(f"   错误: {task.error}")
            report_parts.append("")
        
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        
        report_parts.append(f"\n总结: {completed} 个任务完成, {failed} 个任务失败")
        
        return "\n".join(report_parts)

    def get_task_status(self) -> Dict[str, str]:
        """获取所有任务的状态"""
        return {task.task_id: task.status.value for task in self.tasks}

    def get_task_result(self, task_id: str) -> Any:
        """获取指定任务的结果"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task.result
        return None

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
