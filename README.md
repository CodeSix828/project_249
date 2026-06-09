# Project 249 - 轻量级Agent框架

**Project 249** 是一个轻量级的Python Agent开发框架，旨在帮助开发者快速构建、部署和管理AI Agent应用。

## 特性

- 🚀 **轻量高效**: 最小依赖，快速上手
- 🔄 **多种Agent模式**: 支持SimpleChat、ReAct、PlanExecute等多种Agent范式
- 🛠️ **灵活的工具系统**: 支持自定义工具和预设工具
- 🧠 **记忆系统**: 短期记忆和长期记忆支持
- 📦 **向量存储**: 支持ChromaDB和JSON双后端
- 🔗 **多Agent协作**: AgentHub支持多Agent协同工作
- ⚡ **错误处理**: 完善的异常捕获、超时控制和降级策略
- 📊 **结构化日志**: 灵活的日志系统，支持自定义处理器

## 安装

```bash
pip install project-249
```

或从源码安装:

```bash
git clone https://github.com/CodeSix828/project_249.git
cd project_249
pip install -e .
```

## 快速开始

### 基础对话

```python
from project_249 import SimpleChatAgent

# 创建Agent
agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=True
)

# 运行
response = agent.chat("你好，介绍一下你自己")
print(response)
```

### ReAct Agent

```python
from project_249 import ReActAgent

# 创建带工具的Agent
agent = ReActAgent(
    max_iterations=10,
    verbose=True
)

# 运行
response = agent.chat("北京今天天气怎么样？")
print(response)
```

### Plan-Execute Agent

```python
from project_249 import PlanExecuteAgent

# 创建Agent
agent = PlanExecuteAgent(
    max_retries=3,
    verbose=True
)

# 运行复杂任务
response = agent.chat("帮我创建一个项目文件夹，并查询北京天气")
print(response)
```

## 核心模块

### Agent 模块

| Agent类型 | 描述 |
|-----------|------|
| `SimpleChatAgent` | 简单对话Agent，直接调用LLM |
| `ReActAgent` | 实现Thought-Action-Observation推理循环 |
| `PlanExecuteAgent` | 计划-执行-监控模式 |
| `AgentHub` | 多Agent协作系统 |

### LLM 模块

支持 DeepSeek 系列模型，提供完善的错误处理和超时控制：

- `DeepSeekAdapter`: 主对话模型适配器
- `DeepSeekCallTool`: 工具选择模型适配器

错误类型：
- `LLMTimeoutError`: 请求超时
- `LLMAuthError`: 认证失败
- `LLMRateLimitError`: 速率限制
- `LLMError`: 其他LLM错误

### 工具系统

预设工具:

- `weather_query`: 天气查询
- `mkdir`: 创建目录
- `check_path`: 检查路径（支持自定义预览行数）
- `write_to_file`: 写入文件（支持覆盖/追加模式）
- `get_current_time`: 获取当前时间

### 记忆系统

- `ShortTermMemory`: 短期记忆，支持多种策略（截断、摘要、压缩）
- `LongTermMemory`: 长期记忆，支持持久化和语义检索

### 日志系统

```python
from project_249.utils.logger import Logger, LogCategory

# 自定义日志处理器
def my_handler(level, message, category):
    print(f"[{category.value if category else 'general'}] {message}")

logger = Logger(
    verbose=True,
    handler=my_handler,
    enabled_categories={LogCategory.AGENT, LogCategory.TOOL, LogCategory.ERROR}
)

# 控制特定类别的日志
logger.enable_log("llm")  # 启用LLM日志
logger.disable_log("memory")  # 禁用Memory日志
```

## 配置

创建 `.env` 文件或设置环境变量：

```bash
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek-chat
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/CodeSix828/project_249.git

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
