import os
import pytest

from project_249.config import Settings, load_settings


class TestSettings:
    def test_default_model_name(self):
        settings = Settings(DEEPSEEK_API_KEY="test")
        assert settings.DEEPSEEK_MODEL_NAME == "deepseek-v4-flash"

    def test_baidu_api_key_spelling(self):
        settings = Settings(DEEPSEEK_API_KEY="test")
        assert hasattr(settings, "BAIDU_API_KEY")
        assert not hasattr(settings, "BAIDU_API_KE")

    def test_embedding_effective_key_with_separate_key(self):
        settings = Settings(
            DEEPSEEK_API_KEY="deepseek_key",
            EMBEDDING_API_KEY="embedding_key",
        )
        assert settings.EMBEDDING_EFFECTIVE_KEY == "embedding_key"

    def test_embedding_effective_key_fallback(self):
        settings = Settings(
            DEEPSEEK_API_KEY="deepseek_key",
            EMBEDDING_API_KEY="",
        )
        assert settings.EMBEDDING_EFFECTIVE_KEY == "deepseek_key"

    def test_embedding_use_deepseek(self):
        settings = Settings(DEEPSEEK_API_KEY="test")
        assert settings.EMBEDDING_USE_DEEPSEEK is True

    def test_embedding_use_separate_provider(self):
        settings = Settings(
            DEEPSEEK_API_KEY="test",
            EMBEDDING_API_KEY="separate_key",
        )
        assert settings.EMBEDDING_USE_DEEPSEEK is False

    def test_is_tool_available_missing_key(self):
        settings = Settings(
            DEEPSEEK_API_KEY="test",
            GAODE_TIANQI_API_KEY="",
        )
        assert settings.is_tool_available("weather_query") is False

    def test_is_tool_available_with_key(self):
        settings = Settings(
            DEEPSEEK_API_KEY="test",
            GAODE_TIANQI_API_KEY="some_key",
        )
        assert settings.is_tool_available("weather_query") is True

    def test_is_tool_available_unknown_tool(self):
        settings = Settings(DEEPSEEK_API_KEY="test")
        assert settings.is_tool_available("unknown_tool") is True


class TestLoadSettings:
    def test_load_with_override(self):
        settings = load_settings(
            env_path=None,
            use_env_vars=False,
            override={
                "DEEPSEEK_API_KEY": "custom_key",
                "DEEPSEEK_MODEL_NAME": "custom-model",
            },
        )
        assert settings.DEEPSEEK_API_KEY == "custom_key"
        assert settings.DEEPSEEK_MODEL_NAME == "custom-model"

    def test_missing_required_key(self):
        with pytest.raises(ValueError):
            load_settings(
                env_path="g:/AI_agent/project_249/config/nonexistent.env",
                use_env_vars=False,
                override={},
            )
