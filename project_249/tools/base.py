import json

from .weather_query import weather_query
from .square_calculate import square_calculate
from .mkdir import mkdir
from .write_to_file import write_to_file
from .check_path import check_path, check_multiple_paths, find_files

TOOL_POOL = {
    "weather_query": weather_query,
    "square_calculate": square_calculate,
    "mkdir": mkdir,
    "write_to_file": write_to_file,
    "check_path": check_path,
    "check_multiple_paths": check_multiple_paths,
    "find_files": find_files,
}

def parse_function_call(message):
    messages = {}
    # tool_calls 为工具选择的结果
    if not message.tool_calls:
        return messages
    for tool_call in message.tool_calls:
        #大模型提取出的工具入参
        args = tool_call.function.arguments
        if tool_call.function.name in TOOL_POOL:
            function = TOOL_POOL[tool_call.function.name]
            function_result = function(**json.loads(args))
        else:
            function_result = {"error": "未找到可调用的函数"}
        # 将工具调用的结果封装成message, 参与下一次大模型调用
        messages = {
            "role": "tool",
            "content": f"{json.dumps(function_result)}",
            "tool_call_id": tool_call.id
        }
    return messages

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


