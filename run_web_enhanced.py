import gradio as gr
from project_249 import (
    SimpleChatAgent,
    ReActAgent,
    PlanExecuteAgent,
    AgentHub,
    AgentInfo,
    AgentRole,
    Task,
    TaskStatus,
)

# 全局变量管理当前状态
current_agent = None
agent_hub = None

def create_agent(agent_type, memory_type, verbose):
    """创建指定类型的 Agent"""
    global current_agent
    
    if agent_type == "SimpleChat":
        current_agent = SimpleChatAgent(memory_type, verbose=verbose)
    elif agent_type == "ReAct":
        current_agent = ReActAgent(memory_type, verbose=verbose)
    elif agent_type == "PlanExecute":
        current_agent = PlanExecuteAgent(memory_type, verbose=verbose)
    
    return f"已创建 {agent_type} Agent (记忆类型: {memory_type})"

def chat_with_agent(message, history, agent_type):
    """与 Agent 对话，支持流式输出"""
    global current_agent
    
    if current_agent is None:
        yield "请先选择 Agent 类型并创建 Agent！"
        return
    
    # 初始化响应
    full_response = []
    
    # 使用流式输出
    for chunk in current_agent.chat_stream(message):
        full_response.append(chunk)
        yield ''.join(full_response)

def get_task_status():
    """获取 PlanExecuteAgent 的任务状态（用于可视化）"""
    global current_agent
    
    if current_agent is None or not hasattr(current_agent, "get_task_status"):
        return "请先创建 PlanExecute Agent 并执行任务"
    
    status = current_agent.get_task_status()
    result = []
    for task_id, status_str in status.items():
        status_emoji = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️",
        }.get(status_str, "❓")
        
        # 尝试获取任务描述
        task_desc = task_id
        if hasattr(current_agent, "tasks"):
            for task in current_agent.tasks:
                if task.task_id == task_id:
                    task_desc = f"{task_id}: {task.description}"
                    if task.result:
                        task_desc += f"\n结果: {str(task.result)[:200]}"
                    break
        
        result.append(f"{status_emoji} {task_desc}")
    
    return "\n".join(result) if result else "暂无任务"

def get_memory_status():
    """获取当前记忆状态"""
    global current_agent
    
    if current_agent is None:
        return "请先创建 Agent"
    
    if hasattr(current_agent, "memory"):
        memory_type = type(current_agent.memory).__name__
        
        # 尝试获取历史记录数量
        count = 0
        if hasattr(current_agent.memory, "historys"):
            count = len(current_agent.memory.historys)
        elif hasattr(current_agent.memory, "documents"):
            count = len(current_agent.memory.documents)
        
        return f"记忆类型: {memory_type}\n历史记录数: {count}"
    
    return "未知记忆状态"

# Gradio 界面
with gr.Blocks(title="AI Agent 可视化平台") as demo:
    gr.Markdown("# 🏗️ AI Agent 可视化平台")
    gr.Markdown("支持多种 Agent 模式、任务执行可视化、记忆查看")
    
    with gr.Row():
        with gr.Column(scale=2):
            # Agent 配置区域
            with gr.Group():
                gr.Markdown("## 🤖 Agent 配置")
                agent_type = gr.Dropdown(
                    choices=["SimpleChat", "ReAct", "PlanExecute"],
                    value="SimpleChat",
                    label="Agent 类型"
                )
                memory_type = gr.Dropdown(
                    choices=["short_term", "long_term"],
                    value="short_term",
                    label="记忆类型"
                )
                verbose = gr.Checkbox(value=False, label="显示日志")
                create_btn = gr.Button("创建 Agent", variant="primary")
                agent_status = gr.Textbox(label="Agent 状态")
            
            # 聊天界面
            chatbot = gr.Chatbot(label="对话")
            msg = gr.Textbox(label="输入消息")
            clear = gr.Button("清空")
            
        with gr.Column(scale=1):
            # 可视化区域
            with gr.Tab("任务状态"):
                task_status = gr.Textbox(label="执行中的任务", lines=15)
                refresh_task_btn = gr.Button("刷新任务状态")
                
            with gr.Tab("记忆状态"):
                memory_status = gr.Textbox(label="当前记忆状态", lines=10)
                refresh_memory_btn = gr.Button("刷新记忆状态")
                
            with gr.Tab("说明"):
                gr.Markdown("""
                ## 使用说明
                
                1. 选择 Agent 类型和记忆类型
                2. 点击"创建 Agent"
                3. 在下方输入框输入消息开始对话
                
                ## Agent 类型
                
                - **SimpleChat**: 基础对话 Agent
                - **ReAct**: 推理-行动循环 Agent
                - **PlanExecute**: 规划-执行 Agent
                
                ## 记忆类型
                
                - **short_term**: 短期记忆（会话级）
                - **long_term**: 长期记忆（持久化）
                """)
    
    # 事件绑定
    create_btn.click(
        create_agent,
        inputs=[agent_type, memory_type, verbose],
        outputs=[agent_status]
    )
    
    msg.submit(chat_with_agent, inputs=[msg, chatbot, agent_type], outputs=[chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    
    refresh_task_btn.click(get_task_status, outputs=[task_status])
    refresh_memory_btn.click(get_memory_status, outputs=[memory_status])


if __name__ == "__main__":
    demo.launch()
