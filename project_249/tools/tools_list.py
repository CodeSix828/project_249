tools = [
{
    "type": "function",
    "function": {
        "name": "weather_query",
        "description": "根据用户提供的城市信息查询天气",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "需要查询天气的城市名"
                }
            },
            "required": ["location"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "square_calculate",
        "description": "计算用户输入数值的平方",
        "parameters": {
            "type": "object",
            "properties": {
                "num": {
                    "type": "integer",
                    "description": "需要计算平方的数值"
                }
            },
            "required": ["num"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "mkdir",
        "description": "创建目录",
        "parameters": {
            "type": "object",  # ✅ 必须是 "object"
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径"
                }
            },
            "required": ["path"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "write_to_file",
        "description": "将文本内容写入文件。默认所有文件操作都在工作目录中进行，可以使用相对路径（如 'test/note.txt'）。支持覆盖或追加写入模式。",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "文件路径。可以是相对路径（基于工作目录）如 './data/note.txt'，或绝对路径（仅在必要时使用）如 'G:/Virtual Desktop Environment/note.txt'"
                },
                "content": {
                    "type": "string",
                    "description": "要写入文件的文本内容"
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "是否覆盖原有文件内容 (True=覆盖，False=追加)，默认为 True",
                    "default": True
                }
            },
            "required": ["filepath", "content"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "check_path",
        "description": "检查文件或文件夹是否存在，并返回详细信息（类型、大小、权限、内容预览等）。支持读取完整或部分文件内容。",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "要检测的路径，可以是相对路径（如 'data/config.json'）或绝对路径"
                },
                "preview_lines": {
                    "type": "integer",
                    "description": "文件内容预览行数，默认为5行",
                    "default": 5
                },
                "preview_full": {
                    "type": "boolean",
                    "description": "是否预览完整文件内容（仅在需要完整信息时设为True），默认为False",
                    "default": False
                }
            },
            "required": ["filepath"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "find_files",
        "description": "在指定目录中搜索匹配模式的文件",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "要搜索的目录路径"
                },
                "pattern": {
                    "type": "string",
                    "description": "文件名模式，支持通配符，如 '*.txt' 查找所有txt文件，'test*' 查找以test开头的文件",
                    "default": "*"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "是否递归搜索子目录",
                    "default": True
                }
            },
            "required": ["directory"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "获取当前系统时间和日期",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_current_date",
        "description": "获取当前日期（简化版）",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
]
