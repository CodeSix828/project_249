from project_249 import SimpleChatAgent
from project_249.utils import stream_print_no_delay


def main():
    agent = SimpleChatAgent("short_term", "SUMMARY", verbose=True)
    print("开始对话（输入 'exit' 或 'quit' 退出）")

    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("对话结束")
            break
        
        agent.memory.retrieval(user_input)
        
        print("AI: ", end="", flush=True)
        stream_print_no_delay(agent.chat_stream(user_input))


if __name__ == "__main__":
    main()
