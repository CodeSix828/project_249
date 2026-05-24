import os
import pytest


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key_for_testing")
    yield


@pytest.fixture
def temp_env(monkeypatch):
    def _set_env(env_dict):
        for key, value in env_dict.items():
            monkeypatch.setenv(key, value)
    return _set_env
