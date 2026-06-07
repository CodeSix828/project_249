from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MessageType(Enum):
    """消息类型"""
    TASK = "task"           # 任务消息
    REPLY = "reply"         # 回复消息
    STATUS = "status"       # 状态更新
    QUERY = "query"         # 查询消息
    BROADCAST = "broadcast" # 广播消息


class MessageSemantic(Enum):
    """消息语义标签"""
    REQUEST = "request"      # 请求
    INFORM = "inform"        # 通知
    CONFIRM = "confirm"     # 确认
    DENY = "deny"           # 拒绝
    QUERY = "query"         # 查询
    RESPONSE = "response"   # 响应


@dataclass
class AgentMessage:
    """
    Agent 消息协议。
    
    用于 Agent 之间通信的标准消息格式。
    """
    sender: str                          # 发送方 Agent 名称
    receiver: str                         # 接收方 Agent 名称（空=广播）
    msg_type: MessageType                 # 消息类型
    semantic: MessageSemantic             # 消息语义
    content: Any                          # 消息内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 消息ID
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "msg_type": self.msg_type.value,
            "semantic": self.semantic.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    def __str__(self) -> str:
        return f"[{self.msg_type.value}] {self.sender} -> {self.receiver}: {str(self.content)[:100]}"


class AgentRole(Enum):
    """Agent 角色"""
    COORDINATOR = "coordinator"  # 协调者
    PLANNER = "planner"          # 规划者
    EXECUTOR = "executor"        # 执行者
    REVIEWER = "reviewer"        # 审核者
    SPECIALIST = "specialist"    # 专家


@dataclass
class AgentInfo:
    """
    Agent 信息描述。
    
    描述一个 Agent 的身份、角色和接口。
    """
    name: str                           # Agent 名称
    role: AgentRole                     # Agent 角色
    description: str                     # Agent 描述
    input_types: List[str] = field(default_factory=list)   # 接收的消息类型
    output_types: List[str] = field(default_factory=list)   # 发送的消息类型
    capabilities: List[str] = field(default_factory=list)   # Agent 能力
    agent_instance: Any = None          # Agent 实例


class AgentHub:
    """
    多 Agent 协作系统核心。
    
    AgentHub 负责：
    - 管理多个 Agent 的生命周期
    - 处理 Agent 之间的消息路由
    - 定义消息协议和语义
    - 协调多 Agent 协作任务
    
    使用示例：
    ```python
    # 创建 AgentHub
    hub = AgentHub()
    
    # 注册 Agent
    hub.register_agent(AgentInfo(
        name="planner",
        role=AgentRole.PLANNER,
        description="任务规划专家",
        input_types=["user_request"],
        output_types=["task_plan"],
        capabilities=["task_decomposition", "dependency_analysis"],
    ))
    
    # 注册 Agent 实例
    planner_agent = ReActAgent()
    hub.register_agent_instance("planner", planner_agent)
    
    # 发送消息
    hub.send_message(AgentMessage(
        sender="user",
        receiver="planner",
        msg_type=MessageType.TASK,
        semantic=MessageSemantic.REQUEST,
        content="帮我查询北京天气并规划明天的活动",
    ))
    
    # 获取消息
    messages = hub.get_messages("planner")
    ```
    """

    def __init__(self, name: str = "AgentHub"):
        """
        初始化 AgentHub。
        
        参数：
            name: AgentHub 名称
        """
        self.name = name
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queues: Dict[str, List[AgentMessage]] = {}
        self.message_history: List[AgentMessage] = []
        
    def register_agent(self, agent_info: AgentInfo):
        """
        注册 Agent 信息。
        
        参数：
            agent_info: Agent 信息对象
        """
        if agent_info.name in self.agents:
            raise ValueError(f"Agent {agent_info.name} 已经注册")
        
        self.agents[agent_info.name] = agent_info
        self.message_queues[agent_info.name] = []
        
    def register_agent_instance(self, agent_name: str, agent_instance: Any):
        """
        注册 Agent 实例。
        
        参数：
            agent_name: 已注册的 Agent 名称
            agent_instance: Agent 实例
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} 未注册")
        
        self.agents[agent_name].agent_instance = agent_instance
    
    def unregister_agent(self, agent_name: str):
        """
        注销 Agent。
        
        参数：
            agent_name: Agent 名称
        """
        if agent_name not in self.agents:
            return
        
        del self.agents[agent_name]
        if agent_name in self.message_queues:
            del self.message_queues[agent_name]
    
    def send_message(self, message: AgentMessage):
        """
        发送消息。
        
        消息会被路由到接收方的消息队列。
        
        参数：
            message: 消息对象
        """
        # 记录到历史
        self.message_history.append(message)
        
        # 如果是广播消息，发送给所有 Agent
        if message.receiver == "" or message.msg_type == MessageType.BROADCAST:
            for agent_name in self.agents:
                if agent_name != message.sender:  # 不发给自己
                    self.message_queues[agent_name].append(message)
        else:
            # 发送给指定 Agent
            if message.receiver in self.message_queues:
                self.message_queues[message.receiver].append(message)
    
    def get_messages(self, agent_name: str, clear: bool = False) -> List[AgentMessage]:
        """
        获取 Agent 的消息队列。
        
        参数：
            agent_name: Agent 名称
            clear: 是否在获取后清空队列
            
        返回：
            消息列表
        """
        if agent_name not in self.message_queues:
            return []
        
        messages = self.message_queues[agent_name]
        
        if clear:
            self.message_queues[agent_name] = []
        
        return messages
    
    def get_message_history(self, agent_name: Optional[str] = None) -> List[AgentMessage]:
        """
        获取消息历史。
        
        参数：
            agent_name: 如果指定，只返回与该 Agent 相关的消息
            
        返回：
            消息历史列表
        """
        if agent_name is None:
            return self.message_history
        
        return [
            msg for msg in self.message_history
            if msg.sender == agent_name or msg.receiver == agent_name
        ]
    
    def clear_history(self):
        """清空消息历史"""
        self.message_history.clear()
    
    def get_agent_info(self, agent_name: str) -> Optional[AgentInfo]:
        """
        获取 Agent 信息。
        
        参数：
            agent_name: Agent 名称
            
        返回：
            Agent 信息对象，如果不存在返回 None
        """
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[AgentInfo]:
        """
        列出所有注册的 Agent。
        
        返回：
            Agent 信息列表
        """
        return list(self.agents.values())
    
    def create_task_message(
        self,
        sender: str,
        receiver: str,
        content: Any,
        semantic: MessageSemantic = MessageSemantic.REQUEST,
        metadata: Optional[Dict] = None,
    ) -> AgentMessage:
        """
        创建任务消息的便捷方法。
        
        参数：
            sender: 发送方
            receiver: 接收方
            content: 消息内容
            semantic: 消息语义
            metadata: 元数据
            
        返回：
            消息对象
        """
        return AgentMessage(
            sender=sender,
            receiver=receiver,
            msg_type=MessageType.TASK,
            semantic=semantic,
            content=content,
            metadata=metadata or {},
        )
    
    def create_reply_message(
        self,
        sender: str,
        receiver: str,
        content: Any,
        original_message_id: Optional[str] = None,
        semantic: MessageSemantic = MessageSemantic.RESPONSE,
        metadata: Optional[Dict] = None,
    ) -> AgentMessage:
        """
        创建回复消息的便捷方法。
        
        参数：
            sender: 发送方
            receiver: 接收方
            content: 消息内容
            original_message_id: 原消息 ID
            semantic: 消息语义
            metadata: 元数据
            
        返回：
            消息对象
        """
        metadata = metadata or {}
        if original_message_id:
            metadata["original_message_id"] = original_message_id
        
        return AgentMessage(
            sender=sender,
            receiver=receiver,
            msg_type=MessageType.REPLY,
            semantic=semantic,
            content=content,
            metadata=metadata,
        )
    
    def broadcast_message(
        self,
        sender: str,
        content: Any,
        semantic: MessageSemantic = MessageSemantic.INFORM,
        metadata: Optional[Dict] = None,
    ) -> AgentMessage:
        """
        创建广播消息的便捷方法。
        
        参数：
            sender: 发送方
            content: 消息内容
            semantic: 消息语义
            metadata: 元数据
            
        返回：
            消息对象
        """
        return AgentMessage(
            sender=sender,
            receiver="",  # 空表示广播
            msg_type=MessageType.BROADCAST,
            semantic=semantic,
            content=content,
            metadata=metadata or {},
        )
    
    def route_message(self, message: AgentMessage) -> List[str]:
        """
        路由消息到相关 Agent。
        
        基于消息内容和 Agent 的角色进行智能路由。
        
        参数：
            message: 消息对象
            
        返回：
            接收消息的 Agent 名称列表
        """
        receivers = []
        
        # 如果明确指定了接收方
        if message.receiver:
            receivers.append(message.receiver)
            return receivers
        
        # 智能路由：根据消息类型和语义
        if message.msg_type == MessageType.TASK:
            # 任务消息优先发送给协调者或规划者
            for agent_info in self.agents.values():
                if agent_info.role in [AgentRole.COORDINATOR, AgentRole.PLANNER]:
                    if agent_info.name != message.sender:
                        receivers.append(agent_info.name)
        
        elif message.msg_type == MessageType.QUERY:
            # 查询消息发送给专家
            for agent_info in self.agents.values():
                if agent_info.role == AgentRole.SPECIALIST:
                    if agent_info.name != message.sender:
                        receivers.append(agent_info.name)
        
        elif message.msg_type == MessageType.STATUS:
            # 状态消息发送给协调者
            for agent_info in self.agents.values():
                if agent_info.role == AgentRole.COORDINATOR:
                    if agent_info.name != message.sender:
                        receivers.append(agent_info.name)
        
        # 如果没有找到特定接收方，广播给所有人
        if not receivers:
            for agent_name in self.agents:
                if agent_name != message.sender:
                    receivers.append(agent_name)
        
        return receivers
    
    def execute_multi_agent_task(
        self,
        task: str,
        agent_sequence: List[str],
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        执行多 Agent 协作任务。
        
        按照指定顺序依次调用 Agent，最终汇总结果。
        
        参数：
            task: 初始任务描述
            agent_sequence: Agent 调用顺序
            context: 初始上下文
            
        返回：
            最终结果和每个 Agent 的输出
        """
        results = {
            "task": task,
            "agent_outputs": {},
            "final_result": None,
        }
        
        current_content = task
        context = context or {}
        
        for agent_name in agent_sequence:
            if agent_name not in self.agents:
                continue
            
            agent_info = self.agents[agent_name]
            
            if agent_info.agent_instance is None:
                continue
            
            # 为 Agent 构建输入消息
            input_message = self.create_task_message(
                sender="system",
                receiver=agent_name,
                content={
                    "task": current_content,
                    "context": context,
                    "history": results["agent_outputs"],
                },
            )
            
            # 调用 Agent
            try:
                if hasattr(agent_info.agent_instance, "chat"):
                    output = agent_info.agent_instance.chat(input_message.content["task"])
                else:
                    output = str(agent_info.agent_instance)
                
                results["agent_outputs"][agent_name] = output
                current_content = output
                
            except Exception as e:
                results["agent_outputs"][agent_name] = {"error": str(e)}
        
        results["final_result"] = current_content
        return results
