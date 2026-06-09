# 示例脚本使用说明

这个目录包含了多个示例脚本，帮助你快速了解和使用 AI Agent 项目。

## 运行前准备

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置 API 密钥**

在 `config/.env` 文件中配置你的 API 密钥（参考 `config/.env.example`）：

```env
DEEPSEEK_API_KEY=sk-your_api_key_here
DEEPSEEK_MODEL_NAME=deepseek-v4-flash
```

## 示例列表

### 1. 最简单的对话
**文件**: `01_simple_chat.py`

展示如何创建基本的 Agent 并进行对话，包括测试短期记忆。

```bash
python examples/01_simple_chat.py
```

### 2. 流式输出
**文件**: `02_stream_output.py`

展示如何使用真正的流式输出（不是逐字打印的假流式）。

```bash
python examples/02_stream_output.py
```

### 3. 日志控制
**文件**: `03_log_control.py`

展示如何控制日志输出，适合作为第三方库使用时。
- 静默模式
- 只启用特定日志分类
- 自定义日志处理器
- 动态修改日志配置

```bash
python examples/03_log_control.py
```

### 4. RAG 系统
**文件**: `04_rag_system.py`

展示完整的 RAG 流程：
- 文档分块
- 向量存储
- 语义检索
- 基于检索结果生成回答

```bash
python examples/04_rag_system.py
```

### 5. 长期记忆
**文件**: `05_long_term_memory.py`

展示长期记忆的使用：
- 持久化存储
- 语义检索
- 验证重启后记忆仍然存在

```bash
python examples/05_long_term_memory.py
```

### 6. ReAct Agent
**文件**: `06_react_agent.py`

展示 ReAct（思考-行动-观察）模式：
- 自主决策是否调用工具
- 多步推理过程
- 实时信息获取

```bash
python examples/06_react_agent.py
```

### 7. Plan-Execute Agent
**文件**: `07_plan_execute.py`

展示 规划-执行 模式：
- 将复杂任务分解为子任务
- 任务依赖关系管理
- 执行状态和结果报告

```bash
python examples/07_plan_execute.py
```

### 8. 错误处理与降级策略
**文件**: `08_error_handling.py`

展示框架的健壮性：
- 超时处理
- 认证失败处理
- 降级策略
- 优雅的异常恢复

```bash
python examples/08_error_handling.py
```

## 推荐学习顺序

1. **01_simple_chat.py** - 了解基本用法
2. **02_stream_output.py** - 了解流式输出
3. **03_log_control.py** - 了解日志控制
4. **06_react_agent.py** - 了解 ReAct 模式
5. **07_plan_execute.py** - 了解 Plan-Execute 模式
6. **08_error_handling.py** - 了解错误处理
7. **04_rag_system.py** - 了解 RAG 系统
8. **05_long_term_memory.py** - 了解长期记忆

## 注意事项

- 示例 4 和 5 需要有效的 API 密钥（会调用 Embedding 和 LLM）
- 所有示例使用临时目录，运行结束后会自动清理
- 实际使用时，请将数据存储到持久化目录
