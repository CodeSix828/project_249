import json

from .weather_query import weather_query
from .square_calculate import square_calculate
from .mkdir import mkdir
from .write_to_file import write_to_file
from .check_path import check_path, check_multiple_paths, find_files
from .get_time import get_current_time, get_current_date

TOOL_POOL = {
    "weather_query": weather_query,
    "square_calculate": square_calculate,
    "mkdir": mkdir,
    "write_to_file": write_to_file,
    "check_path": check_path,
    "check_multiple_paths": check_multiple_paths,
    "find_files": find_files,
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
}

def parse_function_call(message):
    tool_messages = []
    if not message.tool_calls:
        return tool_messages
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        raw_args = tool_call.function.arguments

        try:
            args = json.loads(raw_args)
        except (json.JSONDecodeError, TypeError):
            tool_messages.append({
                "role": "tool",
                "content": json.dumps({"error": f"参数解析失败: {raw_args}"}),
                "tool_call_id": tool_call.id,
            })
            continue

        if tool_name not in TOOL_POOL:
            tool_messages.append({
                "role": "tool",
                "content": json.dumps({"error": f"未找到工具: {tool_name}"}),
                "tool_call_id": tool_call.id,
            })
            continue

        function = TOOL_POOL[tool_name]
        try:
            function_result = function(**args)
        except Exception as e:
            function_result = {
                "error": f"{type(e).__name__}: {e}"
            }

        tool_messages.append({
            "role": "tool",
            "content": json.dumps(function_result),
            "tool_call_id": tool_call.id,
        })
    return tool_messages

'''
from ..llms.deepseek_function_call import DeepSeekCallTool
from tools_list import tools
def function_call(user_query):
    messages = [{"role": "user", "content": user_query}]
    llm_tool = DeepSeekCallTool
    #1.工具选择，参数提取
    response = llm_tool.call_llm(messages, tools)
    #2.具体工具调用
    tool_messages = parse_function_call(response)
    messages.extend(tool_messages)
    #3.用户输入+工具调用结果，再次调用大模型生成结果
    response = llm_tool.call_llm(messages, tools)
    return response.content



user_query = "贵港当前天气怎么样？"
print(function_call(user_query))
'''
