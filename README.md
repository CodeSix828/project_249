# AI Agent 项目

一个功能完整的 AI Agent 框架，支持检索增强生成（RAG）、长短期记忆、工具调用和流式输出。

## 功能特点

### 🤖 多类型 Agent 模式
- **SimpleChatAgent**：基础对话 Agent
- **ReActAgent**：推理-行动循环模式（Thought-Action-Observation）
- **PlanExecuteAgent**：规划-执行-监控模式
- **AgentHub**：多 Agent 协作系统，支持消息路由和角色分工

### 🧠 核心功能
- **LLM 适配层**：统一的大语言模型接口，目前支持 DeepSeek（兼容 OpenAI 格式）
- **真正的流式输出**：不是逐字打印的假流式，而是真正的 SSE 流式传输
- **工具调用**：Agent 可自主调用预设工具完成任务
- **自由扩展**：基于抽象基类即可实现自定义 Agent

### 📚 RAG 系统
- **文档分块**：支持字符分块、段落分块、句子分块多种策略
- **向量存储**：支持 ChromaDB（高性能，默认）和 JSON 文件（兼容旧版）
- **智能检索**：支持向量相似度检索和混合检索（向量+关键词）
- **相似度阈值**：可设置过滤低相关度结果

### 🧠 记忆系统
- **短期记忆**：支持截断、滑动窗口、摘要等策略
- **长期记忆**：持久化存储，支持语义检索和自动摘要
- **灵活配置**：可在两种记忆类型间自由切换

### 📋 日志系统
- **六大分类**：agent、tool、memory、llm、warn、error
- **分类过滤**：可动态启用/禁用特定日志分类
- **静默模式**：支持作为第三方库时完全静默输出
- **自定义回调**：可传入自定义日志处理器

### 🔧 预设工具
- `weather_query`：高德天气查询
- `square_calculate`：平方计算（示例）
- `mkdir`：创建目录
- `write_to_file`：写入文件
- `check_path` / `check_multiple_paths`：路径检查
- `find_files`：文件查找

## 环境要求

- Python 3.8 或更高版本（推荐 3.10+）
- 支持 Windows / macOS / Linux

## 安装步骤

```bash
# 克隆项目
git clone https://github.com/CodeSix828/project_249.git
cd project_249

# 安装依赖
pip install -r requirements.txt
```

### 依赖说明

| 依赖包 | 用途 |
|--------|------|
| `openai>=1.0.0` | 大语言模型调用（DeepSeek 兼容 OpenAI 格式） |
| `pydantic>=2.0.0` | 数据验证和配置管理 |
| `python-dotenv>=1.0.0` | 环境变量管理 |
| `requests>=2.31.0` | HTTP 请求处理 |
| `tiktoken>=0.5.0` | Token 计数 |
| `numpy>=1.20.0` | 数值计算（向量相似度） |
| `chromadb>=0.4.0` | 高性能向量数据库 |
| `pytest>=7.0.0` | 单元测试框架（开发用） |

## 配置说明

在 `config/` 目录下创建 `.env` 文件（可参考 `.env.example`）：

```env
# ========== API 配置 ==========
# DeepSeek API 密钥（必填，用于 LLM 对话）
DEEPSEEK_API_KEY=sk-your_api_key_here
# DeepSeek API 基础 URL
DEEPSEEK_BASE_URL=https://api.deepseek.com
# DeepSeek 模型名称（推荐 deepseek-v4-flash，旧模型将于 2026 年 7 月 24 日退役）
DEEPSEEK_MODEL_NAME=deepseek-v4-flash

# ========== 可选工具配置 ==========
# 百度识图（可选，用于图像识别工具）
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here

# 高德天气（可选，用于天气查询工具）
GAODE_TIANQI_API_KEY=your_amap_weather_api_key_here

# ========== Embedding 配置 ==========
# Embedding 模型提供者（可选，不配置则使用 DEEPSEEK_API_KEY）
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL_NAME=text-embedding-3-small
```

**注意**：
- `EMBEDDING_API_KEY` 不配置时会自动使用 `DEEPSEEK_API_KEY`
- `EMBEDDING_BASE_URL` 不配置时会自动使用 `DEEPSEEK_BASE_URL`

## 快速开始

### 最简单的对话

```python
from agent import SimpleChatAgent

# 创建 Agent
# 参数说明：
# - memory_type: "short_term" 短期记忆 或 "long_term" 长期记忆
# - verbose: 是否显示日志（作为第三方库时可设为 False）
agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=True
)

# 开始对话
response = agent.chat("你好，请介绍一下你自己")
print(response)
```

### 流式输出

```python
from agent import SimpleChatAgent

agent = SimpleChatAgent(memory_type="short_term", verbose=False)

# 流式输出（逐字打印）
for chunk in agent.chat_stream("写一首关于春天的诗"):
    print(chunk, end="", flush=True)
print()
```

### ReAct 模式 Agent（推理-行动循环）

```python
from agent import ReActAgent

# 创建 ReAct Agent
agent = ReActAgent(
    memory_type="short_term",
    verbose=True,
    max_iterations=10,  # 最大循环次数防止无限循环
)

# 执行任务
response = agent.chat("查询北京今天的天气")
print(response)
```

### Plan-Execute 模式 Agent（规划-执行）

```python
from agent import PlanExecuteAgent

# 创建 Plan-Execute Agent
agent = PlanExecuteAgent(
    memory_type="short_term",
    verbose=True,
    max_retries=3,
)

# 执行任务（会自动分解为子任务）
response = agent.chat("帮我规划北京三日游行程")
print(response)

# 查看任务执行状态
status = agent.get_task_status()
print(status)
```

### AgentHub 多 Agent 协作

```python
from agent import (
    AgentHub,
    AgentInfo,
    AgentRole,
    MessageType,
    MessageSemantic,
    AgentMessage,
)
from agent import SimpleChatAgent, ReActAgent

# 1. 创建 AgentHub
hub = AgentHub()

# 2. 注册 Agent 信息
hub.register_agent(AgentInfo(
    name="planner",
    role=AgentRole.PLANNER,
    description="任务规划专家",
    input_types=["user_request"],
    output_types=["task_plan"],
    capabilities=["task_decomposition", "dependency_analysis"],
))

hub.register_agent(AgentInfo(
    name="executor",
    role=AgentRole.EXECUTOR,
    description="任务执行专家",
    input_types=["task_plan"],
    output_types=["task_result"],
    capabilities=["tool_use", "task_execution"],
))

# 3. 注册 Agent 实例
planner_agent = ReActAgent(verbose=False)
executor_agent = SimpleChatAgent(verbose=False)

hub.register_agent_instance("planner", planner_agent)
hub.register_agent_instance("executor", executor_agent)

# 4. 发送消息
message = hub.create_task_message(
    sender="user",
    receiver="planner",
    content="帮我规划北京三日游",
    semantic=MessageSemantic.REQUEST,
)
hub.send_message(message)

# 5. 获取消息并处理
messages = hub.get_messages("planner", clear=True)
for msg in messages:
    print(f"收到消息: {msg}")
```

### 向量数据库（ChromaDB）

```python
from storage.database import Database

# 使用 ChromaDB（默认，高性能）
db = Database(
    store_path="data/my_db",
    backend="chroma",  # 默认值
    collection_name="my_collection",
)

# 或使用 JSON（兼容旧版）
db = Database(
    store_path="data/my_db",
    backend="json",
)

# 添加文档
chunks = ["文档1", "文档2", "文档3"]
db.add_documents(chunks)

# 检索
results = db.query("相关文档", k=2)
print(results)
```

## 详细使用指南

### 一、Agent 基础

#### 1. 创建 Agent

```python
from agent import SimpleChatAgent
from memory.base import Strategy

# 基本用法
agent = SimpleChatAgent(
    memory_type="short_term",  # 或 "long_term"
    verbose=True,              # 是否显示日志
)

# 完整参数
agent = SimpleChatAgent(
    memory_type="short_term",
    compare_type=Strategy.SUMMARY,  # 记忆策略
    verbose=True,
    stream_output=True,             # 是否启用流式输出
)
```

#### 2. 记忆策略

短期记忆支持以下策略（`Strategy` 枚举）：

| 策略 | 值 | 说明 |
|------|-----|------|
| `TRUNCATION` | 0 | 简单截断，删除最旧的消息 |
| `SLIDING_WINDOW` | 1 | 滑动窗口，保留最近的 N 条消息 |
| `SUMMARY` | 2 | 摘要策略，对旧消息进行摘要压缩 |
| `REFINE` | 3 | 精炼策略 |
| `MAP_REDUCE` | 4 | 映射归约策略 |
| `MAP_RANK` | 5 | 映射排序策略 |

长期记忆默认使用 `MAP_REDUCE` 策略。

#### 3. 日志控制

```python
from agent import SimpleChatAgent

# 方式一：初始化时指定
agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=True,
    enabled_logs=["agent", "error"],  # 只启用这两类日志
)

# 方式二：动态修改
agent.set_verbose(False)              # 完全静默
agent.set_enabled_logs(["llm", "memory"])  # 动态调整
agent.enable_log("tool")              # 启用某类
agent.disable_log("warn")             # 禁用某类

# 查看当前启用的日志
print(agent.get_enabled_logs())
```

#### 4. 自定义日志回调

```python
from agent import SimpleChatAgent

def my_log_handler(level, message, category):
    """
    自定义日志处理器
    适合作为第三方库时，将日志转发到应用的日志系统
    """
    print(f"[{category.value}] {message}")

agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=True,
    log_handler=my_log_handler,
)
```

### 二、RAG 系统使用

#### 1. 基础流程

```python
from storage.RAG.text_splitter import SentenceTextSplitter
from storage.database import Database
from chains.rag_chain import create_rag_chain

# Step 1: 准备文档并分块
splitter = SentenceTextSplitter(chunk_size=500, chunk_overlap=50)

# 从文本分块
text = "这是一段很长的文档内容..."
chunks = splitter.split_text(text)

# 从文件分块
from storage.RAG.text_splitter import split_file_content
chunks = split_file_content("path/to/document.txt")

# Step 2: 创建数据库并存储
db = Database(store_path="data/my_knowledge_base")
db.add_documents(chunks)  # 批量添加（高效）

# 或逐条添加
# for chunk in chunks:
#     db.add(chunk)

# Step 3: 创建 RAG 链并查询
chain = create_rag_chain(
    database=db,
    k=3,  # 返回最相关的 3 个文档
    similarity_threshold=0.5,  # 相似度阈值
)

# 普通查询
answer = chain.invoke("根据文档回答：这个项目有哪些功能？")
print(answer)

# 流式查询
for chunk in chain.invoke_stream("请详细介绍 RAG 系统"):
    print(chunk, end="", flush=True)
print()

# 获取回答和上下文（便于调试）
result = chain.invoke_with_context("RAG 如何实现？")
print("回答:", result["answer"])
print("使用的上下文:")
for doc, score in result["contexts"]:
    print(f"  [相似度 {score:.2f}] {doc[:100]}...")
```

#### 2. 文档分块策略选择

```python
from storage.RAG.text_splitter import (
    TextSplitter,
    CharacterTextSplitter,
    SentenceTextSplitter,
)

# 1. 简单字符分块（最基础）
splitter = TextSplitter(chunk_size=1000, chunk_overlap=100)

# 2. 段落分块（优先在段落边界分割）
splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separator="\n\n",  # 段落分隔符
)

# 3. 句子分块（推荐，保持语义完整）
splitter = SentenceTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
```

#### 3. 混合检索（向量 + 关键词）

```python
from chains.rag_chain import create_rag_chain

chain = create_rag_chain(
    database=db,
    k=3,
    use_hybrid=True,           # 启用混合检索
    keyword_weight=0.3,        # 关键词权重（0.0-1.0）
)

answer = chain.invoke("用户的问题")
```

### 三、记忆系统

#### 1. 短期记忆

```python
from memory.short_term import ShortTermMemory
from memory.base import Strategy

# 创建短期记忆
memory = ShortTermMemory(
    strategy=Strategy.SLIDING_WINDOW,
    window_size=5,      # 滑动窗口大小
    max_token_num=2000, # 最大 token 数（截断策略用）
)

# 添加消息
memory.add({"role": "user", "content": "你好"})
memory.add({"role": "assistant", "content": "你好！有什么可以帮助你的？"})

# 检索（会自动应用策略）
history = memory.retrieval()
print(history)
```

#### 2. 长期记忆

```python
from memory.long_term import LongTermMemory
from memory.base import Strategy

# 创建长期记忆
ltm = LongTermMemory(
    strategy=Strategy.MAP_REDUCE,
    store_path="data/long_term_memory",
    single_max_token_num=500,
)

# 添加记忆
ltm.add("用户喜欢的颜色是蓝色")

# 添加带元数据的记忆
ltm.add_with_metadata(
    "用户生日是1月1日",
    {"source": "2024-01-01对话", "importance": "high"}
)

# 检索相关记忆
memories = ltm.retrieval("用户喜欢什么", k=3)
print(memories)

# 获取带相似度分数的结果
results = ltm.retrieval_with_scores("用户生日", k=3)
for mem, score in results:
    print(f"[相似度 {score:.2f}] {mem}")

# 格式化上下文
print(ltm.format_for_context())

# 其他操作
print(f"记忆总数: {ltm.count()}")
# ltm.clear()  # 清空所有记忆（警告：不可恢复）
```

### 四、工具调用

#### 1. 查看可用工具

```python
from tools.base import TOOL_POOL

print("可用工具:", list(TOOL_POOL.keys()))
```

#### 2. 注册自定义工具

参考 `tools/` 目录下的现有工具实现：

```python
# tools/my_tool.py
def my_custom_tool(param1: str, param2: int) -> dict:
    """
    工具描述（用于 LLM 理解工具用途）
    
    参数：
        param1: 参数1描述
        param2: 参数2描述
        
    返回：
        结果字典
    """
    try:
        # 工具逻辑
        result = do_something(param1, param2)
        return {"success": True, "result": result}
    except Exception as e:
        return {"error": True, "message": str(e)}
```

然后在 `tools/base.py` 中注册：

```python
from tools.my_tool import my_custom_tool

TOOL_POOL = {
    # ... 现有工具
    "my_custom_tool": my_custom_tool,
}
```

## 架构说明

```
project_249/
├── agent/                  # Agent 实现
│   ├── base.py             # BaseAgent 抽象基类
│   ├── simple_chat.py      # SimpleChatAgent 实现
│   ├── react_agent.py      # ReAct 模式 Agent
│   ├── plan_execute.py     # 规划执行模式 Agent
│   ├── hub.py              # AgentHub 多 Agent 协作系统
│   └── __init__.py
├── llms/                   # LLM 适配层
│   ├── base.py             # BaseLLM 抽象基类
│   ├── deepseek_adapter.py # DeepSeek 适配器
│   └── deepseek_embedding.py  # DeepSeek Embedding
├── memory/                 # 记忆系统
│   ├── base.py             # 基础定义和策略枚举
│   ├── short_term.py       # 短期记忆
│   ├── long_term.py        # 长期记忆
│   └── summarizer.py       # 摘要生成器
├── storage/                # 存储层
│   ├── database.py         # 向量数据库（支持 ChromaDB/JSON）
│   └── RAG/                # RAG 组件
│       ├── text_splitter.py    # 文档分块器
│       ├── embeddings.py       # Embedding 服务
│       ├── retriever.py        # 检索器
│       └── vector_store.py     # 向量存储
├── chains/                 # 链实现
│   ├── rag_chain.py        # RAG 链
│   └── reflection_chain.py # 反思链
├── tools/                  # 工具系统
│   ├── base.py             # 工具注册和调用
│   ├── tools_list.py       # 工具定义
│   ├── weather_query.py    # 天气查询
│   ├── file_ops.py         # 文件操作
│   └── ...                 # 其他工具
├── config/                 # 配置管理
│   ├── settings.py         # Pydantic 配置
│   ├── .env.example        # 环境变量模板
│   └── .env                # 你的配置（不提交到 git）
├── utils/                  # 工具函数
│   ├── logger.py           # 统一日志系统
│   ├── token_counter.py    # Token 计数
│   └── typewriter.py       # 打字机效果（旧版流式）
├── prompts/                # 提示词
│   ├── personas.py         # 角色设定
│   └── system_prompts.py   # 系统提示词
├── tests/                  # 单元测试
│   ├── conftest.py         # pytest 配置
│   ├── test_config.py      # 配置测试
│   ├── test_memory.py      # 记忆测试
│   ├── test_tools.py       # 工具测试
│   ├── test_logger.py      # 日志测试
│   ├── test_agent.py       # Agent 测试
│   └── test_text_splitter.py  # 分块器测试
├── requirements.txt        # 依赖列表
├── run.py                  # 命令行运行入口
├── run_web.py              # Web 服务入口
└── README.md               # 本文档
```

## 单元测试

### 运行测试

```bash
# 运行所有测试
pytest -v

# 运行特定测试文件
pytest tests/test_memory.py -v

# 运行特定测试
pytest tests/test_text_splitter.py::TestSentenceTextSplitter -v

# 查看覆盖率
pytest --cov=storage/RAG --cov-report=term-missing
```

### 测试覆盖

- ✅ 配置模块（11 个测试）
- ✅ 记忆系统（8 个测试）
- ✅ 工具系统（8 个测试）
- ✅ 日志系统（11 个测试）
- ✅ Agent（7 个测试）
- ✅ 文档分块器（14 个测试）

**总计：58 个测试全部通过**

## 作为第三方库使用

### 静默模式

```python
from agent import SimpleChatAgent

# 作为第三方库，完全静默
agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=False,  # 不输出任何日志
)

# 或使用自定义日志处理器
def my_handler(level, message, category):
    # 转发到你的应用日志系统
    app_logger.log(level.value, f"[{category.value}] {message}")

agent = SimpleChatAgent(
    memory_type="short_term",
    verbose=True,
    log_handler=my_handler,
    enabled_logs=["error"],  # 只接收错误日志
)
```

### 按需启用日志

```python
agent = SimpleChatAgent("short_term", verbose=False)

# 调试时临时启用
agent.set_verbose(True)
agent.set_enabled_logs(["llm", "tool"])

# 调试完成后关闭
agent.set_verbose(False)
```

## 完整示例

### 示例 1：带 RAG 的对话

```python
from agent import SimpleChatAgent
from storage.RAG.text_splitter import SentenceTextSplitter
from storage.database import Database
from chains.rag_chain import create_rag_chain

# 1. 准备知识库
knowledge = """
AI Agent 实验室是一个研究 AI Agent 的项目。
主要功能包括：RAG 检索增强生成、长短期记忆、工具调用。
支持流式输出和静默模式，适合作为第三方库使用。
"""

splitter = SentenceTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = splitter.split_text(knowledge)

db = Database(store_path="data/example_kb")
db.add_documents(chunks)

# 2. 创建 RAG 链
rag_chain = create_rag_chain(database=db, k=2)

# 3. 询问问题
answer = rag_chain.invoke("这个项目有哪些主要功能？")
print(answer)
```

### 示例 2：使用长期记忆的对话

```python
from agent import SimpleChatAgent

# 创建使用长期记忆的 Agent
agent = SimpleChatAgent(
    memory_type="long_term",
    verbose=True,
)

# 对话
agent.chat("我叫张三，喜欢蓝色")
agent.chat("我的生日是 1 月 1 日")

# 过一段时间后（重启程序后仍然记得）
response = agent.chat("我喜欢什么颜色？")
print(response)  # 应该回答蓝色

response = agent.chat("我的生日是什么时候？")
print(response)  # 应该回答 1 月 1 日
```

## 常见问题

### Q1: 安装依赖时出错怎么办？

**A**: 请先升级 pip：
```bash
pip install --upgrade pip
```

如果仍然出错，尝试使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 如何获取 API 密钥？

**A**: 
- DeepSeek: 访问 https://platform.deepseek.com/ 注册并创建 API Key
- 高德天气: 访问 https://lbs.amap.com/ 申请 Web 服务 API Key
- 百度识图: 访问 https://ai.baidu.com/ 申请图像识别 API

### Q3: 如何扩展自己的 Agent？

**A**: 继承 `BaseAgent` 抽象基类并实现 `chat` 方法：

```python
from agent.base import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # 自定义初始化
    
    def chat(self, user_input: str) -> str:
        # 实现你的对话逻辑
        return "你的回答"
```

### Q4: RAG 检索结果不准确怎么办？

**A**: 可以尝试以下方法：
1. 调整 `chunk_size` 和 `chunk_overlap`
2. 尝试不同的分块策略（推荐 `SentenceTextSplitter`）
3. 调整 `k` 值（检索数量）
4. 使用混合检索（`use_hybrid=True`）
5. 提高文档质量，确保内容语义完整

### Q5: 如何清空数据库？

**A**: 
```python
from storage.database import Database

db = Database(store_path="data/my_kb")
db.clear()  # 会删除磁盘文件
```

### Q6: 流式输出如何在 Web 应用中使用？

**A**: `chat_stream()` 返回一个迭代器，可用于 Server-Sent Events (SSE)：

```python
from flask import Flask, Response
from agent import SimpleChatAgent

app = Flask(__name__)
agent = SimpleChatAgent("short_term", verbose=False)

@app.route('/chat')
def chat():
    def generate():
        for chunk in agent.chat_stream("用户问题"):
            yield f"data: {chunk}\n\n"
    return Response(generate(), mimetype='text/event-stream')
```

## 已修复的问题

### 安全问题
- ✅ API 密钥硬编码 → 改为通过 `.env` 加载
- ✅ 创建 `.env.example` 模板

### Bug 修复
- ✅ `len(self, self.historys)` 语法错误 → `len(self.historys)`
- ✅ 字典列表 join 错误 → 新增 `_messages_to_text()`
- ✅ `MAP_REDUCK` 拼写错误 → `MAP_REDUCE`
- ✅ `DEEPSEEL_MODEL_NAME` 拼写错误 → `DEEPSEEK_MODEL_NAME`
- ✅ `BAIDU_API_KE` 拼写错误 → `BAIDU_API_KEY`
- ✅ `find_files` 工具未注册 → 添加到 `TOOL_POOL`
- ✅ `json(open(...))` 错误 → `json.load(open(...))`
- ✅ 硬编码 Windows 路径 → 使用相对路径
- ✅ 工具调用只返回最后一个结果 → 返回完整列表
- ✅ `TRUNCATTON` 拼写错误 → `TRUNCATION`

### 新增功能
- ✅ 统一日志系统（6 大分类，支持过滤）
- ✅ 真正的 LLM 流式输出
- ✅ 静默模式和自定义日志回调
- ✅ 完整的 RAG 系统（分块、存储、检索、生成）
- ✅ 完善的长期记忆
- ✅ 58 个单元测试
- ✅ ReAct 模式 Agent
- ✅ Plan-Execute 模式 Agent
- ✅ AgentHub 多 Agent 协作系统
- ✅ ChromaDB 向量数据库支持

## 更新日志

### v1.1.0 (2026-06-07)
- 新增 ReActAgent（推理-行动循环模式）
- 新增 PlanExecuteAgent（规划-执行-监控模式）
- 新增 AgentHub 多 Agent 协作系统
- 新增 ChromaDB 向量数据库支持
- 修复工具调用和拼写 bug
- 完善文档和示例

### v1.0.0 (2026-05-24)
- 完成 RAG 系统实现
- 完善长期记忆模块
- 添加详细的中文注释
- 58 个单元测试全部通过

### v0.9.0 (2026-05-23)
- 修复记忆系统多个 bug
- 实现统一日志系统
- 实现真正的流式输出
- 搭建单元测试框架

### v0.8.0
- 初始版本
- 基本 Agent 框架
- 工具调用系统
- 基础记忆系统

## 参与贡献

欢迎提交 Issue 或 Pull Request！

提交代码前请确保：
1. 所有测试通过：`pytest -v`
2. 代码有适当的中文注释
3. 遵循现有代码风格

## 许可证

MIT © 2026 CodeSix828
