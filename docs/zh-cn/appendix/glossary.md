# 术语表

> 本术语表整理了 nanobot 教程中的核心概念和技术术语，按字母顺序排列。

---

## A

### Agent
AI 代理，能够感知环境、做出决策并采取行动的智能系统。在 nanobot 中，Agent 是指能够多轮对话、调用工具、维护记忆的 LLM 应用。

### AgentLoop
nanobot 的核心引擎，负责管理对话历史（messages）、处理工具调用、组装 System Prompt。源码位置：`nanobot/agent/loop.py`

**类比：** 就像一个会议主持人，记录发言历史，协调不同发言者（LLM、工具），确保会议顺利进行。

---

## B

### Bootstrap 文件
启动配置文件，在 nanobot 中指 `SOUL.md`、`AGENTS.md`、`USER.md`、`TOOLS.md` 这四个文件。每次对话时都会被读取并注入到 System Prompt 中。

---

## C

### CLI (Command Line Interface)
命令行界面，通过终端执行命令与程序交互。nanobot 提供两种 CLI 模式：
- `nanobot agent` - 交互式对话
- `nanobot gateway` - 持续运行的服务

### Context Window
上下文窗口，LLM 一次能处理的最大 token 数量。例如 GPT-4 是 128K tokens。超出窗口的内容会被截断或需要压缩。

---

## D

### Dream
nanobot 的长期记忆管理系统，负责将对话历史归档、提取关键信息、生成摘要。类似人类的"做梦"过程，整理白天的经历。

---

## F

### Frontmatter
文件头部的元数据区域，用 `---` 包裹，采用 YAML 格式。在 nanobot 的 Skill 中用于定义 name、description 等属性。

**示例：**
```yaml
---
name: exchange-rate
description: Query real-time exchange rates
---
```

---

## G

### Gateway
网关模式，`nanobot gateway` 是一个持续运行的服务，通过 MessageBus 接入多个聊天平台（Telegram、Discord 等）。

**对比 CLI 模式：**
- CLI：单次对话，对话结束即退出
- Gateway：持续运行，等待消息推送

---

## L

### LLM (Large Language Model)
大型语言模型，如 GPT-4、Claude、DeepSeek 等。nanobot 通过 Provider 适配不同的 LLM API。

---

## M

### Memory
记忆系统，nanobot 使用分层记忆：
- **短期记忆**：当前对话的 messages 列表
- **长期记忆**：`memory/MEMORY.md` 中的持久化信息
- **历史归档**：`memory/history.jsonl` 中的旧对话摘要

### MessageBus
消息总线，nanobot 的核心通信层，连接 Gateway 和 AgentLoop。支持多平台消息路由、格式转换、错误处理。

**设计目的：** 解耦平台接入和 Agent 逻辑，支持同时接入多个聊天平台。

---

## P

### Provider
LLM 提供商适配器，负责和不同 LLM API 通信，屏蔽接口差异。源码位置：`nanobot/providers/`

**支持的 Provider：**
- OpenRouter
- OpenAI
- Claude/Anthropic
- DeepSeek
- Ollama（本地）

### Prompt
提示词，发送给 LLM 的指令文本。在 nanobot 中分为：
- **System Prompt**：定义 Bot 的身份、规则、能力
- **User Prompt**：用户的输入消息
- **Assistant Prompt**：Bot 的回复

---

## R

### ReAct Loop
Reasoning + Acting 循环，Agent 的核心工作模式：
1. **Reason**：分析当前状态，决定下一步
2. **Act**：执行工具调用或回复用户
3. **Observe**：观察结果，更新状态
4. 重复直到任务完成

---

## S

### Session
会话，一次完整的对话过程。包含 messages 历史、上下文状态、配置信息。

### Skill
技能，教会 Bot 如何做特定事情的 Markdown 文件。采用渐进式加载机制，按需读取完整内容。

**核心设计：**
- **第 1 层**：所有 Skill 的 name + description（始终加载）
- **第 2 层**：匹配 Skill 的 SKILL.md 正文（按需加载）
- **第 3 层**：Skill 的 scripts/、references/ 等资源（按需加载）

### System Prompt
系统提示词，定义 Bot 的"人格"和"规则"。在 nanobot 中由以下部分组装：
```
固定身份 (nanobot)
+ AGENTS.md (行为规则)
+ SOUL.md (性格价值观)
+ USER.md (用户画像)
+ TOOLS.md (工具约束)
+ Memory (长期记忆)
+ Skills Summary (技能摘要)
```

---

## T

### Token
文本单元，LLM 处理文本的最小单位。1 个 token 约等于 4 个英文字符或 1.5 个中文字符。

**示例：**
- "Hello, world!" ≈ 4 tokens
- "你好，世界！" ≈ 6 tokens

### Tool
工具，Bot 可以调用的外部能力。nanobot 内置的工具包括：
- `exec` - 执行命令
- `read_file` / `write_file` - 文件读写
- `web_search` / `web_fetch` - 网络搜索和抓取

---

## W

### Workspace
工作区，`~/.nanobot/workspace/` 目录，存放 Bot 的配置和数据：
```
workspace/
├── AGENTS.md
├── SOUL.md
├── USER.md
├── TOOLS.md
├── memory/
│   ├── MEMORY.md
│   └── history.jsonl
└── skills/
```

---

## 符号与缩写

### API Key
应用程序接口密钥，用于身份验证和访问控制。在 nanobot 中用于调用 LLM API。

### JSON (JavaScript Object Notation)
一种轻量级数据交换格式，nanobot 的配置文件 `config.json` 使用该格式。

### Markdown
一种轻量级标记语言，nanobot 的配置文件（SOUL.md 等）和 Skill 都使用 Markdown 格式。

### YAML (YAML Ain't Markup Language)
一种数据序列化格式，nanobot 的 Skill frontmatter 使用 YAML 格式。

---

## 相关资源

- [第 1 章：5 分钟跑起来](../zero/01-quick-start.md) - 核心概念首次出现
- [第 2 章：让 Bot 有个性](../zero/02-soul.md) - System Prompt 组装
- [第 3 章：教 Bot 新技能](../zero/03-skills.md) - Skill 渐进式加载
- [进阶营第 1 章](../hero/01-simplest-agent.md) - Provider 和 Session
- [进阶营第 4 章](../hero/04-message-bus.md) - MessageBus 架构

---

## 贡献

如果你发现术语解释不清晰或缺少重要术语，欢迎提交 Issue 或 Pull Request。
