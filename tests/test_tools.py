import pytest
from project_249 import TOOL_POOL
from project_249.tools.square_calculate import square_calculate
from project_249.tools.mkdir import mkdir
from project_249.tools.weather_query import weather_query
import tempfile
import os


class TestToolPool:
    def test_tool_pool_contains_all_tools(self):
        expected_tools = [
            "weather_query",
            "square_calculate",
            "mkdir",
            "write_to_file",
            "check_path",
            "check_multiple_paths",
            "find_files",
        ]
        for tool in expected_tools:
            assert tool in TOOL_POOL

    def test_tool_pool_functions_are_callable(self):
        for tool_name, func in TOOL_POOL.items():
            assert callable(func)


class TestSquareCalculate:
    def test_positive_number(self):
        assert square_calculate(5) == 25

    def test_zero(self):
        assert square_calculate(0) == 0

    def test_negative_number(self):
        assert square_calculate(-3) == 9

    def test_float(self):
        assert square_calculate(2.5) == 6.25


class TestWeatherQueryWithoutKey:
    def test_returns_error_without_key(self, monkeypatch):
        from project_249.config import settings as global_settings
        
        monkeypatch.setattr(global_settings, "GAODE_TIANQI_API_KEY", "")
        
        result = weather_query("北京")
        assert "error" in result
        assert "未配置" in result["message"] or "缺少" in result["message"]


class TestMkdir:
    def test_creates_directory_in_workdir(self, tmp_path):
        from project_249.tools.config import WORKDIR_ROOT
        
        test_dir = os.path.join(WORKDIR_ROOT, "test_mkdir_temp_12345")
        
        try:
            result = mkdir("test_mkdir_temp_12345")
            assert "已创建" in result
            assert os.path.exists(test_dir)
        finally:
            if os.path.exists(test_dir):
                os.rmdir(test_dir)


class TestParseFunctionCall:
    def test_tool_pool_has_find_files(self):
        assert "find_files" in TOOL_POOL
