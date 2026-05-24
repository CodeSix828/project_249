import gradio as gr
from project_249 import SimpleChatAgent

agent = SimpleChatAgent("short_term", "SUMMARY", verbose=False)


def chat_with_agent(message, history):
    agent.memory.retrieval(message)
    
    full_response = []
    for chunk in agent.chat_stream(message):
        full_response.append(chunk)
        yield ''.join(full_response)


demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="AIagent实验室助手",
    description="基于DeepSeek的智能体，支持记忆和工具调用",
)

if __name__ == "__main__":
    demo.launch()
