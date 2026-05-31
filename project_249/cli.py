import sys
import argparse

try:
    from . import (
        SimpleChatAgent,
        check_config,
        run_setup_wizard,
        handle_api_error,
    )
    from .memory.base import Strategy
except ImportError:
    from project_249 import (
        SimpleChatAgent,
        check_config,
        run_setup_wizard,
        handle_api_error,
    )
    from project_249.memory.base import Strategy


DEFAULT_CONFIG = {
    "memory_type": "short_term",
    "verbose": False,
    "enabled_logs": None,
}


def print_banner():
    print("=" * 60)
    print("  Project 249 - AI Agent Framework")
    print("=" * 60)
    print()


def check_or_setup_config():
    config = check_config()
    if config["is_valid"]:
        return True
    print("=" * 60)
    print("配置检测")
    print("=" * 60)
    print()
    if config["api_key_configured"]:
        print("  检测到 API 密钥，但密钥格式无效")
        print(f"  配置文件: {config['env_path']}")
    else:
        print("  未检测到有效的 API 密钥配置")
    print()
    print("请选择：")
    print("  1. 运行配置向导（推荐）")
    print("  2. 继续使用（可能会报错）")
    print("  3. 退出")
    print()
    choice = input("请选择 [1-3，默认1]: ").strip()
    if choice == "3":
        print("已退出。请先配置 API 密钥后再运行。")
        return False
    if choice == "2":
        return True
    try:
        run_setup_wizard()
    except KeyboardInterrupt:
        print("\n\n配置已取消。")
        return False
    return True


def agent_config_wizard():
    config = DEFAULT_CONFIG.copy()
    print("=" * 60)
    print("智能体配置向导")
    print("=" * 60)
    print()

    print("\n步骤 1: 选择记忆类型")
    print("  1. 短期记忆（默认）- 对话期间保存")
    print("  2. 长期记忆 - 持久化存储，跨会话保存")
    print()
    choice = input("请选择 [1-2，默认1]: ").strip()
    if choice == "2":
        config["memory_type"] = "long_term"
    else:
        config["memory_type"] = "short_term"

    print("\n步骤 2: 日志设置")
    print("  1. 无日志（默认）")
    print("  2. 基础日志（显示 agent 活动")
    print("  3. 调试日志（显示所有日志")
    print()
    choice = input("请选择 [1-3，默认1]: ").strip()
    if choice == "2":
        config["verbose"] = True
        config["enabled_logs"] = ["agent", "error"]
    elif choice == "3":
        config["verbose"] = True
        config["enabled_logs"] = ["agent", "llm", "tool", "error"]
    else:
        config["verbose"] = False
        config["enabled_logs"] = None

    print("\n步骤 3: 已保存配置:")
    print(f"  记忆类型: {config['memory_type']}")
    print(f"  详细日志: {config['verbose']}")
    if config["enabled_logs"]:
        print(f"  日志类别: {config['enabled_logs']}")
    print()
    print("=" * 60)
    print()
    return config


def cli_mode(config):
    print("=" * 60)
    print("命令行模式")
    print("=" * 60)
    print("开始对话（输入 'exit' 或 'quit' 或 'q' 退出\n")

    agent = SimpleChatAgent(
        memory_type=config["memory_type"],
        verbose=config["verbose"],
        enabled_logs=config["enabled_logs"],
    )

    while True:
        try:
            user_input = input("你: ")
        except (EOFError, KeyboardInterrupt):
            print("\n\n对话结束")
            break
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\n对话结束")
            break
        if not user_input.strip():
            continue
        try:
            agent.memory.retrieval(user_input)
            print("AI: ", end="", flush=True)
            for chunk in agent.chat_stream(user_input):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            handle_api_error(e)
            break


def web_mode(config):
    try:
        import gradio as gr
    except ImportError:
        print("=" * 60)
        print("  未安装 gradio，无法使用网页模式")
        print("=" * 60)
        print()
        print("请先安装 gradio:")
        print("  pip install project_249[web]")
        print()
        choice = input("是否安装 gradio？[Y/n]: ").strip().lower()
        if choice in ['', 'y', 'yes']:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio"])
            import gradio as gr
        else:
            print("已取消。请手动安装后重试。")
            return

    print("=" * 60)
    print("网页模式")
    print("=" * 60)
    print()
    print("正在启动网页界面...")
    print("启动后请在浏览器中访问显示的 URL")
    print()

    agent = SimpleChatAgent(
        memory_type=config["memory_type"],
        verbose=config["verbose"],
        enabled_logs=config["enabled_logs"],
    )

    def chat_with_agent(message, history):
        agent.memory.retrieval(message)
        full_response = []
        for chunk in agent.chat_stream(message):
            full_response.append(chunk)
            yield ''.join(full_response)

    demo = gr.ChatInterface(
        fn=chat_with_agent,
        title="Project 249 - AI 助手",
        description="基于 project_249 框架的 AI 助手，支持记忆和流式输出",
    )
    demo.launch(inbrowser=True)


def interactive_menu():
    config = DEFAULT_CONFIG.copy()

    while True:
        print("=" * 60)
        print("欢迎使用 Project 249")
        print("=" * 60)
        print()
        print("当前配置:")
        print(f"  记忆类型: {config['memory_type']}")
        print(f"  详细日志: {'是' if config['verbose'] else '否'}")
        if config["enabled_logs"]:
            print(f"  日志类别: {config['enabled_logs']}")
        print()
        print("=" * 60)
        print()
        print("请选择:")
        print("  1. 运行命令行对话")
        print("  2. 运行网页对话")
        print("  3. 配置智能体")
        print("  4. 配置 API 密钥")
        print("  5. 退出")
        print()
        choice = input("请选择 [1-5，默认1]: ").strip()

        if choice == "5":
            print("再见！")
            return

        if choice == "4":
            run_setup_wizard()
            continue

        if choice == "3":
            config = agent_config_wizard()
            continue

        if not check_or_setup_config():
            return

        if choice == "2":
            web_mode(config)
            return
        else:
            cli_mode(config)
            return


def main():
    parser = argparse.ArgumentParser(
        prog="project-249",
        description="Project 249 - AI Agent Framework",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    subparsers.add_parser("setup", help="运行配置向导")
    subparsers.add_parser("config", help="配置智能体参数")
    subparsers.add_parser("check", help="检查配置状态")

    cli_parser = subparsers.add_parser("cli", help="命令行对话模式")
    cli_parser.add_argument(
        "--memory",
        choices=["short_term", "long_term"],
        default="short_term",
        help="记忆类型（默认: short_term）",
    )
    cli_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志",
    )
    cli_parser.add_argument(
        "--logs",
        nargs="*",
        choices=["agent", "llm", "tool", "error"],
        help="启用的日志类别",
    )

    web_parser = subparsers.add_parser("web", help="网页对话模式")
    web_parser.add_argument(
        "--memory",
        choices=["short_term", "long_term"],
        default="short_term",
        help="记忆类型（默认: short_term）",
    )
    web_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志",
    )
    web_parser.add_argument(
        "--logs",
        nargs="*",
        choices=["agent", "llm", "tool", "error"],
        help="启用的日志类别",
    )

    args = parser.parse_args()

    if args.command == "setup":
        print_banner()
        run_setup_wizard()
        return

    if args.command == "config":
        print_banner()
        agent_config_wizard()
        return

    if args.command == "check":
        print_banner()
        config_status = check_config()
        print(f"配置文件: {config_status['env_path']}")
        print(f"API 密钥已配置: {config_status['api_key_configured']}")
        print(f"配置有效: {config_status['is_valid']}")
        if not config_status["is_valid"]:
            print(f"提示: {config_status['message']}")
        return

    if args.command == "cli":
        print_banner()
        config = DEFAULT_CONFIG.copy()
        config["memory_type"] = args.memory
        config["verbose"] = args.verbose
        if args.logs:
            config["enabled_logs"] = args.logs
        if check_or_setup_config():
            cli_mode(config)
        return

    if args.command == "web":
        print_banner()
        config = DEFAULT_CONFIG.copy()
        config["memory_type"] = args.memory
        config["verbose"] = args.verbose
        if args.logs:
            config["enabled_logs"] = args.logs
        if check_or_setup_config():
            web_mode(config)
        return

    interactive_menu()


if __name__ == "__main__":
    main()
