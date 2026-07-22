# 术语表

> 本术语表以 nanobot v0.2.2 为基线，整理教程中的核心概念。

## A

### Agent

能够接收消息、调用模型与工具、维护会话和持久状态的应用。在 nanobot 中，它不是单独一次 LLM 请求，而是多个运行部件的组合。

### Agent 工作区（Agent Workspace）

由 `agents.defaults.workspace` 配置的实例级持久目录，默认是 `~/.nanobot/workspace/`。它拥有 Agent 的 Bootstrap、Memory、Session、Skill、cron 状态和生成物。CLI 的 `--workspace` 会覆盖这个工作区。

### AgentLoop

面向完整消息生命周期的编排器：选择 Session 和有效工作区、构建上下文、调用执行循环、保存结果并把出站消息交回 Channel。源码类位于 `nanobot/agent/loop.py`。

## B

### Bootstrap 文件

每轮构建 System Prompt 时从有效工作区读取的三个文件：`AGENTS.md`、`SOUL.md`、`USER.md`。文件不存在时跳过。工具约定来自独立的内置 tool contract，不存在第四个自动 Bootstrap 文件。

## C

### Channel

用户消息的传输适配层，例如 CLI、WebUI/WebSocket、Telegram、Discord 或 Slack。Channel 把外部事件转换为统一消息，并负责把出站结果发回原平台。

### CLI（Command Line Interface）

命令行界面。`nanobot agent` 用于本地单次或交互式聊天；`nanobot gateway` 启动持续运行的 Channel 与后台任务。

### Consolidator

当 Session 接近上下文预算时，把较旧且边界完整的消息归档为摘要，并追加到 `memory/history.jsonl` 的组件。它负责“压缩归档”，不等于 Dream 的长期事实整理。

### Context Window

模型一次请求能够处理的输入与输出总预算。具体容量由模型和配置决定；不要用固定字符比例推断所有模型的 token 数。

## D

### Dream

持久记忆整理流程。它读取尚未消费的 `memory/history.jsonl` 条目，整理 Agent 工作区里的 `SOUL.md`、`USER.md` 和 `memory/MEMORY.md`，并通过 GitStore 留下可审计、可恢复的版本。它不管理 `AGENTS.md`。

## F

### Frontmatter

文件开头由 `---` 包裹的 YAML 元数据。Skill 用它声明 `name`、`description`、`always` 和依赖等信息。

```yaml
---
name: exchange-rate
description: Query current exchange rates with validation
---
```

## G

### Gateway

`nanobot gateway` 启动的长运行进程。它连接已启用的 Channel，运行消息编排和后台任务，并提供健康状态入口。

### GitStore

nanobot 用来版本化持久记忆文件的内部存储。Dream 更新后可通过相关命令查看差异或恢复旧状态。

## L

### LLM（Large Language Model）

大型语言模型。nanobot 通过 Provider 统一不同服务的请求、流式输出和工具调用格式。

## M

### Memory

跨会话持久状态的统称：

- `memory/history.jsonl` 保存 Consolidator 追加的历史摘要；
- `memory/MEMORY.md` 保存经 Dream 整理的长期项目事实；
- `SOUL.md` 和 `USER.md` 也是 Dream 可维护的长期知识文件；
- 当前对话的 `session.messages` 属于短期会话状态，不是同一个文件。

### MessageBus

连接 Channel 与 AgentLoop 的异步消息队列。它统一入站和出站消息形状，使传输层不必直接调用推理实现。教程中的 Mini Agent 会保留一个简化模型。

## P

### Project 工作区（Project Workspace）

WebUI 为某个聊天选择的当前项目目录。它会成为当轮工具根和三个 Bootstrap 文件的读取根；Agent 工作区的同名 Bootstrap 不会自动叠加。它不接管 Agent 工作区中的 MemoryStore 与 Dream 状态，项目选择本身也不保证操作系统级隔离。

### Provider

模型服务适配器，负责把 nanobot 请求转换为特定模型 API，并把回复、流式事件和工具调用转换回统一结构。源码位于 `nanobot/providers/`。

### Prompt

发送给模型的上下文。常见角色包括 system、user、assistant 和 tool；Prompt 不等于权限控制。

## R

### ReAct Loop

模型在“决定下一步 → 调用工具 → 观察结果”之间迭代，直到形成最终回复或达到迭代边界的执行模式。

### Recent History

从 `memory/history.jsonl` 读取、尚未被 Dream 游标消费的近期摘要。只有启用注入且存在符合条件的条目时，才会进入 System Prompt。

### Runtime Context

附在当前消息后的运行时元数据，例如当前时间、Channel、Chat ID 和 Sender ID。它被明确标记为 metadata only，不是长期指令。

## S

### Session

某个会话键对应的消息与元数据集合。Channel、聊天 ID 和是否启用 unified session 会影响会话如何隔离；较旧消息可能被 Consolidator 归档。

### Skill

面向特定任务的可复用指令包。通常先向模型提供名称和描述，需要时再读取 `SKILL.md` 正文及脚本、references 等资源；标记为 `always` 的 Skill 可直接进入上下文。

### System Prompt

`ContextBuilder` 组装的系统层上下文。v0.2.2 的主要顺序是：

```text
内置 identity
+ AGENTS.md / SOUL.md / USER.md
+ 内置 tool contract
+ 非模板长期 Memory（存在时）
+ always Skills 正文
+ 其他 Skills 摘要
+ Recent History（符合条件时）
+ Session 归档摘要（存在时）
```

## T

### Token

模型分词器处理文本的单位。不同模型对中文、英文、代码和标点的切分不同，精确数量应使用对应 Provider/模型的计数能力或实际 usage。

### Tool

模型可调用的能力，例如文件操作、命令执行、Web、MCP、cron 或消息发送。是否可用及能访问什么由配置、运行时和工具实现共同决定。

### Tool contract

nanobot 内置并注入 System Prompt 的工具通用协议，说明工具调用、结果处理和边界。它来自源码模板，不是用户工作区里的自动 Bootstrap 文件。

## W

### Workspace

泛指工作目录。阅读教程时要根据语境区分 Agent 工作区和 WebUI 项目工作区：前者拥有持久 Agent 状态，后者描述当前聊天处理的项目范围。

```text
agent-workspace/
├── AGENTS.md
├── SOUL.md
├── USER.md
├── memory/
│   ├── MEMORY.md
│   └── history.jsonl
├── sessions/
└── skills/
```

## 符号与缩写

### API Key

调用模型或外部服务的凭据。应通过环境变量引用或安全的密钥管理方式提供，不应提交到仓库或打印到诊断输出。

### JSON（JavaScript Object Notation）

轻量级数据交换格式。nanobot 的 `config.json` 使用 JSON，并在文档中通常采用 camelCase 字段。

### Markdown

轻量级标记语言。Bootstrap、Memory 和 Skill 的主要教学内容均使用 Markdown。

### YAML（YAML Ain't Markup Language）

Skill frontmatter 使用的数据格式。

## 固定源码依据

- [`ContextBuilder`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/agent/context.py)
- [`MemoryStore` 与 `Consolidator`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/agent/memory.py)
- [`WorkspaceScope`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/security/workspace_access.py)

## 相关资源

- [第 1 章：5 分钟跑起来](../zero/01-quick-start.md)
- [第 2 章：让 Bot 有个性](../zero/02-soul.md)
- [第 3 章：教 Bot 新技能](../zero/03-skills.md)
- [进阶营第 3 章：记忆与上下文](../hero/03-memory-and-context.md)
- [进阶营第 4 章：MessageBus](../hero/04-message-bus.md)
