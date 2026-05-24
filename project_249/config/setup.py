from pathlib import Path
from typing import Optional
import sys
from .settings import (
    BASE_DIR,
    DEFAULT_ENV_PATH,
    Settings,
    load_settings,
    _settings as _global_settings,
)


API_KEY_PLACEHOLDERS = [
    "your_deepseek_api_key_here",
    "sk-your_api_key_here",
    "your_api_key_here",
]

HELP_MESSAGES = {
    "missing_key": """
╔════════════════════════════════════════════════════════════╗
║                    API 密钥未配置！                           ║
╠════════════════════════════════════════════════════════════╣
║  请按以下步骤配置 API 密钥：                                  ║
║                                                             ║
║  方式 1: 运行快捷配置向导                                     ║
║    python -m project_249.config.setup                       ║
║                                                             ║
║  方式 2: 手动配置                                            ║
║    1. 访问 https://platform.deepseek.com/                    ║
║    2. 注册账号并获取 API Key                                  ║
║    3. 在以下位置创建 .env 文件：                               ║
║       {env_path}
║    4. 添加配置：                                              ║
║       DEEPSEEK_API_KEY=sk-你的密钥                            ║
║                                                             ║
║  方式 3: 设置环境变量                                         ║
║    Windows: set DEEPSEEK_API_KEY=sk-你的密钥                  ║
║    Linux/macOS: export DEEPSEEK_API_KEY=sk-你的密钥           ║
╚════════════════════════════════════════════════════════════╝
""",
    "invalid_key": """
╔════════════════════════════════════════════════════════════╗
║                    API 密钥无效！                             ║
╠════════════════════════════════════════════════════════════╣
║  错误原因: {error_message}                                   ║
║                                                             ║
║  请检查以下问题：                                             ║
║  1. API 密钥是否完整（通常以 sk- 开头）                         ║
║  2. 密钥是否已过期或被撤销                                     ║
║  3. 账户余额是否充足                                          ║
║                                                             ║
║  访问 https://platform.deepseek.com/ 查看你的 API Key         ║
║                                                             ║
║  重新配置: python -m project_249.config.setup                ║
╚════════════════════════════════════════════════════════════╝
""",
    "config_success": """
╔════════════════════════════════════════════════════════════╗
║                  配置保存成功！                               ║
╠════════════════════════════════════════════════════════════╣
║  配置文件已保存到:                                           ║
║    {env_path}                                               ║
║                                                             ║
║  现在可以开始使用 AI 助手了！                                 ║
╚════════════════════════════════════════════════════════════╝
""",
}


def get_env_path(custom_path: Optional[Path] = None) -> Path:
    if custom_path:
        return Path(custom_path)
    return DEFAULT_ENV_PATH


def is_valid_api_key(key: str) -> bool:
    if not key or not key.strip():
        return False
    key = key.strip()
    for placeholder in API_KEY_PLACEHOLDERS:
        if placeholder.lower() in key.lower():
            return False
    if not key.startswith("sk-"):
        return False
    return True


def check_config(env_path: Optional[Path] = None) -> dict:
    env_path = get_env_path(env_path)
    result = {
        "is_valid": False,
        "env_path": str(env_path),
        "env_exists": env_path.exists(),
        "api_key_configured": False,
        "api_key_valid": False,
        "error_message": None,
    }

    try:
        settings = load_settings(env_path=str(env_path), use_env_vars=True)
        result["api_key_configured"] = True
        result["api_key_valid"] = is_valid_api_key(settings.DEEPSEEK_API_KEY)
        result["is_valid"] = result["api_key_valid"]
    except ValueError as e:
        result["error_message"] = str(e)
    except Exception as e:
        result["error_message"] = f"未知错误: {e}"

    return result


def show_missing_key_help(env_path: Optional[Path] = None):
    env_path = get_env_path(env_path)
    print(HELP_MESSAGES["missing_key"].format(env_path=str(env_path)))


def show_invalid_key_help(error_message: str = ""):
    print(HELP_MESSAGES["invalid_key"].format(error_message=error_message))


def show_config_success(env_path: Path):
    print(HELP_MESSAGES["config_success"].format(env_path=str(env_path)))


def save_config(
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    model_name: str = "deepseek-v4-flash",
    env_path: Optional[Path] = None,
) -> Path:
    env_path = get_env_path(env_path)
    env_path.parent.mkdir(parents=True, exist_ok=True)

    existing_config = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_config[key.strip()] = value.strip()

    new_config = {
        "DEEPSEEK_API_KEY": api_key.strip(),
        "DEEPSEEK_BASE_URL": base_url,
        "DEEPSEEK_MODEL_NAME": model_name,
    }
    existing_config.update(new_config)

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# API 配置 (由 setup.py 自动生成)\n")
        for key, value in existing_config.items():
            f.write(f"{key}={value}\n")

    return env_path


def run_setup_wizard():
    print("=" * 60)
    print("project_249 配置向导")
    print("=" * 60)
    print()

    current_config = check_config()
    if current_config["api_key_configured"] and current_config["api_key_valid"]:
        print(f"✓ 检测到已配置的 API 密钥")
        print(f"  配置文件: {current_config['env_path']}")
        print()
        choice = input("是否更新配置？[y/N]: ").strip().lower()
        if choice not in ["y", "yes"]:
            print("配置未更改。")
            return

    print()
    print("请输入你的 DeepSeek API Key")
    print("获取地址: https://platform.deepseek.com/")
    print()

    while True:
        api_key = input("API Key: ").strip()
        if is_valid_api_key(api_key):
            break
        print("⚠ 密钥格式无效。DeepSeek API Key 通常以 'sk-' 开头，请重新输入。")
        print()

    print()
    base_url = input(f"API 基础 URL [默认: https://api.deepseek.com]: ").strip()
    if not base_url:
        base_url = "https://api.deepseek.com"

    print()
    model_name = input(f"模型名称 [默认: deepseek-v4-flash]: ").strip()
    if not model_name:
        model_name = "deepseek-v4-flash"

    print()
    env_path_str = input(f"配置文件保存路径 [回车使用默认]: ").strip()
    env_path = Path(env_path_str) if env_path_str else None

    saved_path = save_config(api_key, base_url, model_name, env_path)

    print()
    show_config_success(saved_path)


def handle_api_error(error: Exception, env_path: Optional[Path] = None) -> int:
    error_str = str(error).lower()

    if "401" in error_str or "authentication" in error_str or "invalid" in error_str:
        if "your api key" in error_str:
            show_invalid_key_help("API 密钥无效或已过期")
        else:
            show_missing_key_help(env_path)
        return 1

    if "insufficient" in error_str or "quota" in error_str:
        show_invalid_key_help("账户余额不足或配额已用完")
        return 2

    show_invalid_key_help(str(error))
    return 3


if __name__ == "__main__":
    try:
        run_setup_wizard()
    except KeyboardInterrupt:
        print("\n\n配置已取消。")
        sys.exit(1)
