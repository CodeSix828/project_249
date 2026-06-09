# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-06-09

### Fixed

- **修复"主对话模型"重复前缀bug**: 移除了不必要的消息前缀标记，避免LLM生成内容被重复标记
- **工具调用结果重复前缀**: 移除"内部工具选择模型"等不必要的标记

### Changed

- **LLM模块错误处理增强**: 
  - 添加了超时控制（`timeout`参数）
  - 添加了重试机制（`max_retries`参数）
  - 细化了错误类型（`LLMTimeoutError`、`LLMAuthError`、`LLMRateLimitError`）
  - 添加了`chat_with_fallback`方法，支持降级策略
  - 添加了`validate_connection`方法，验证API连接

- **工具选择模块增强**:
  - 添加了超时控制和重试机制
  - 细化了错误类型（`ToolCallTimeoutError`、`ToolCallAuthError`、`ToolCallRateLimitError`）
  - 添加了`call_llm_with_fallback`方法，支持降级策略
  - 添加了`validate_connection`方法

### Documentation

- 更新了README.md，添加了新特性说明
- 更新了快速开始示例代码
- 添加了错误处理和日志系统的使用说明

## [1.2.1] - 2025-06-08

### Fixed

- **工具调用返回结果修复**: 修改`parse_function_call`函数，返回结果列表而非单个结果
- **TRUNCATTON拼写错误**: 修正为`TRUNCATION`
- **向量相似度注释错误**: 将"欧氏距离"修正为"余弦相似度"
- **PlanExecuteAgent语法错误**: 修正了`ToolCallMessage`类中的括号不匹配问题

### Added

- **write_to_file覆盖写入**: 新增`overwrite`参数，支持覆盖或追加模式
- **check_path读取增强**: 新增`preview_lines`和`preview_full`参数，支持自定义预览行数或读取完整文件
- **get_current_time工具**: 新增获取当前系统时间的工具

## [1.2.0] - 2025-06-07

### Added

- **PlanExecuteAgent**: 实现计划-执行-监控模式的Agent
- **AgentHub**: 多Agent协作系统，支持Agent注册、消息路由和角色协作
- **ChromaDB集成**: 高性能向量数据库支持
- **JSON向量存储**: 兼容旧版的JSON文件存储
- **Gradio可视化界面**: 基于Web的用户界面

## [1.1.0] - 2025-06-06

### Added

- **ReActAgent**: 实现Thought-Action-Observation推理循环
- **长期记忆系统**: 持久化存储和语义检索
- **短期记忆系统**: 支持截断、摘要、压缩等多种策略

## [1.0.0] - 2025-06-05

### Added

- **SimpleChatAgent**: 基础对话Agent
- **LLM模块**: DeepSeek系列模型支持
- **工具系统**: 预设工具和自定义工具支持
- **日志系统**: 结构化日志和自定义处理器
- **配置管理**: 环境变量和配置文件支持
