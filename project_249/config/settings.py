from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import dotenv_values
import os
import sys


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_executable_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_PATH = BASE_DIR / "config" / ".env"

EXE_ENV_PATH = get_executable_dir() / ".env"

ENV_PATH = EXE_ENV_PATH if is_frozen() and EXE_ENV_PATH.exists() else DEFAULT_ENV_PATH


class Settings(BaseModel):
    DEEPSEEK_API_KEY: str = Field(..., description="DeepSeek API密钥（必填，用于LLM对话）")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", description="DeepSeek API基础URL")
    DEEPSEEK_MODEL_NAME: str = Field(default="deepseek-v4-flash", description="DeepSeek模型名称")
    
    BAIDU_API_KEY: str = Field(default="", description="百度API密钥（可选，用于图像识别工具）")
    BAIDU_SECRET_KEY: str = Field(default="", description="百度Secret密钥（可选，用于图像识别工具）")
    GAODE_TIANQI_API_KEY: str = Field(default="", description="高德天气API密钥（可选，用于天气查询工具）")
    
    EMBEDDING_PROVIDER: str = Field(default="openai", description="Embedding模型提供者（openai 或其他）")
    EMBEDDING_API_KEY: str = Field(default="", description="Embedding API密钥（可选，不配置则使用DEEPSEEK_API_KEY）")
    EMBEDDING_BASE_URL: str = Field(default="", description="Embedding API基础URL（可选）")
    EMBEDDING_MODEL_NAME: str = Field(default="text-embedding-3-small", description="Embedding模型名称")
    
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    @property
    def EMBEDDING_USE_DEEPSEEK(self) -> bool:
        return not self.EMBEDDING_API_KEY
    
    @property
    def EMBEDDING_EFFECTIVE_KEY(self) -> str:
        return self.EMBEDDING_API_KEY or self.DEEPSEEK_API_KEY
    
    @property
    def EMBEDDING_EFFECTIVE_URL(self) -> str:
        return self.EMBEDDING_BASE_URL or self.DEEPSEEK_BASE_URL
    
    def is_tool_available(self, tool_name: str) -> bool:
        tool_key_map = {
            "weather_query": "GAODE_TIANQI_API_KEY",
            "baidu": "BAIDU_API_KEY",
            "baidu_secret": "BAIDU_SECRET_KEY",
        }
        key_name = tool_key_map.get(tool_name)
        if key_name is None:
            return True
        return bool(getattr(self, key_name, ""))


def _load_from_env_file(env_path: Path) -> dict:
    if env_path.exists():
        return dotenv_values(env_path)
    return {}


def _load_from_env_vars() -> dict:
    env_vars = {}
    for key in Settings.model_fields.keys():
        value = os.environ.get(key)
        if value is not None:
            env_vars[key] = value
    return env_vars


def load_settings(
    env_path: str | Path | None = None,
    use_env_vars: bool = True,
    override: dict | None = None
) -> Settings:
    configs: dict = {}
    
    if env_path:
        file_config = _load_from_env_file(Path(env_path))
        configs.update(file_config)
    else:
        if is_frozen():
            if EXE_ENV_PATH.exists():
                file_config = _load_from_env_file(EXE_ENV_PATH)
                configs.update(file_config)
            else:
                file_config = _load_from_env_file(DEFAULT_ENV_PATH)
                configs.update(file_config)
        else:
            file_config = _load_from_env_file(DEFAULT_ENV_PATH)
            configs.update(file_config)
    
    if use_env_vars:
        env_config = _load_from_env_vars()
        configs.update(env_config)
    
    if override:
        configs.update(override)
    
    try:
        return Settings(**configs)
    except Exception as e:
        raise ValueError(
            f"配置加载失败: {e}\n"
            f"请确保配置了必要的环境变量（至少需要 DEEPSEEK_API_KEY），或创建 .env 文件。\n"
            f"可参考项目中的 .env.example 文件创建配置。"
        ) from e


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


settings = get_settings()
