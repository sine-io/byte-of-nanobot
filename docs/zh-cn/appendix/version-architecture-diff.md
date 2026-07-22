# 稳定版与 main 架构差异

这份附录回答一个容易混淆的问题：教程里哪些能力可以直接用于稳定版，哪些只是本轮审计到的主线实现。

!!! info "两条固定基线"

    - 操作正文：nanobot **v0.2.2**，固定提交 `e2e75c913f3524d4bc5b23487a4eed5329eef182`。
    - 差异对照：[`main@b189a376`](https://github.com/HKUDS/nanobot/tree/b189a37648e4fa64f662b15de4f78ffd0bab403b)，完整提交 `b189a37648e4fa64f662b15de4f78ffd0bab403b`。

本文只有两种状态：

- **v0.2.2 可用**：可以按教程正文操作；main 可能在内部重构了实现，但不改变这里的稳定版归类。
- **仅 main/未来版本**：只在固定 main 快照中确认；不代表已经发布，也不能直接复制到 v0.2.2 配置或命令中。

!!! warning "这不是升级指南"

    main 是一个移动中的开发分支。本文只描述固定快照与 v0.2.2 的差异，不承诺这些接口会原样进入下一个版本。遇到冲突时，以教程正文的 v0.2.2 步骤为准。

## 一览

| 领域 | 稳定版能力 | main 差异 |
|---|---|---|
| Agent 与项目工作区 | **v0.2.2 可用**：Agent 工作区保存持久状态；WebUI 可为会话选择项目工作区 | **仅 main/未来版本**：远程工作区切换增加非提权判定，模型上下文整形进一步集中 |
| Bootstrap 归属 | **v0.2.2 可用**：选择项目工作区后，`AGENTS.md`、`SOUL.md`、`USER.md` 都从项目根读取 | **仅 main/未来版本**：项目只提供 `AGENTS.md`，`SOUL.md` 与 `USER.md` 改由 Agent 工作区提供 |
| 模型选择 | **v0.2.2 可用**：命名 `modelPresets`、默认预设、回退模型和单次运行覆盖 | **仅 main/未来版本**：`ModelRuntimeResolver` 集中解析不可变的单轮运行时 |
| WebUI | **v0.2.2 可用**：内置 WebUI、WebSocket 会话、工作区与模型设置 | **仅 main/未来版本**：WebUI 可管理独立的 API 后台进程 |
| API 与 SDK | **v0.2.2 可用**：`nanobot serve` 提供 OpenAI 兼容 API，Python SDK 支持普通、流式和单次模型覆盖 | **仅 main/未来版本**：API 增加可选 Bearer 鉴权，非本地监听必须配置密钥 |
| 定时自动化 | **v0.2.2 可用**：cron、Heartbeat 与绑定会话的 WebUI 定时任务 | **仅 main/未来版本**：统一的自动化轮次协调器扩展到本地触发器 |
| 本地触发器 | **v0.2.2 可用**：无；不要在稳定版执行 main 的触发器命令 | **仅 main/未来版本**：`/trigger`、`nanobot trigger` 与工作区内的持久投递队列 |
| Goals 与 Subagents | **v0.2.2 可用**：持续 Goal 与子 Agent 执行框架 | **仅 main/未来版本**：Goal 工具改为创建/更新生命周期，并增加显式授权边界 |
| MCP | **v0.2.2 可用**：stdio、SSE、Streamable HTTP，以及 tool/resource/prompt 包装 | **仅 main/未来版本**：网络目标、日志脱敏、图像产物和工具白名单语义进一步加固 |
| Channel | **v0.2.2 可用**：扁平内置模块，并可从 `nanobot.channels` entry point 加载第三方插件 | **仅 main/未来版本**：内置 Channel 改为自包含包、manifest、运行时与 WebUI 资源契约 |
| 旧 Channel entry point | **v0.2.2 可用**：外部 entry-point 插件仍会加载，内置同名 Channel 优先 | **仅 main/未来版本**：固定快照只告警、不再加载旧 entry point；它不是稳定版插件的兼容替代 |

## 工作区与上下文所有权

### v0.2.2 可用

Agent 工作区是实例级持久目录，拥有 Memory、Session、Skills、cron 状态和 Dream 管理的文件。WebUI 选择的项目工作区是当前会话的工具根；在 v0.2.2 中，它也会成为三个 Bootstrap 文件的共同读取根：

    v0.2.2

    项目工作区
    ├── AGENTS.md ─┐
    ├── SOUL.md   ─┼─> 当前轮 System Prompt
    └── USER.md   ─┘

    Agent 工作区
    ├── memory/
    ├── sessions/
    ├── skills/
    └── cron 状态

因此，教程正文把项目规则、行为策略和用户偏好分别写入项目根的 `AGENTS.md`、`SOUL.md`、`USER.md`，对 v0.2.2 是正确操作。项目工作区仍不是操作系统沙箱，Memory 与 Dream 的归属也没有转移。

### 仅 main/未来版本

固定 main 快照改变了 Bootstrap 的来源：项目工作区只提供 `AGENTS.md`，Agent 工作区提供全局 `SOUL.md` 与 `USER.md`。

    main@b189a376

    项目工作区/AGENTS.md ─────────┐
    Agent 工作区/SOUL.md ─────────┼─> 当前轮 System Prompt
    Agent 工作区/USER.md ─────────┘

main 还在 WebUI 工作区切换中加入“只允许非提权变化”的判定，并把模型可见消息的整形逻辑拆到独立的上下文治理模块。这些变化不应反向改写 v0.2.2 的 Bootstrap 操作步骤，也不等于新增了操作系统级隔离。

固定源码入口：[`ContextBuilder`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/context.py)、[`ContextGovernor`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/context_governance.py)、[`webui/workspaces.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/webui/workspaces.py)。

## 模型、WebUI、API 与 SDK

### v0.2.2 可用

- **v0.2.2 可用**：命名 `modelPresets`、默认预设和 `fallbackModels` 已属于稳定版，不是 main 新功能。
- **v0.2.2 可用**：WebUI 已能管理会话、项目工作区、配置和模型选择。
- **v0.2.2 可用**：`nanobot serve` 已提供 OpenAI 兼容接口；`Nanobot` Python SDK 已支持 `run`、流式运行，以及按次指定模型或模型预设。

### 仅 main/未来版本

- **仅 main/未来版本**：`ModelRuntimeResolver` 把默认模型、预设、SDK 单次覆盖与每轮准入解析到统一的不可变运行时对象。这是内部边界重构，不表示 v0.2.2 缺少模型预设。
- **仅 main/未来版本**：`ApiRuntime` 管理 WebUI 启动的独立 `nanobot serve` 后台进程。
- **仅 main/未来版本**：API 支持可选 Bearer Token；固定快照要求监听 `0.0.0.0` 或 `::` 时配置 API 密钥。不要把该规则误写成 v0.2.2 已有的配置能力。

固定源码入口：[`model_presets.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/model_presets.py)、[`ModelRuntimeResolver`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/model_runtime.py)、[`Nanobot` SDK](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/nanobot.py)、[`ApiRuntime`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/api/runtime.py)、[`api/server.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/api/server.py)。

## 自动化

### v0.2.2 可用

- **v0.2.2 可用**：cron 支持一次、固定间隔和 cron 表达式调度。
- **v0.2.2 可用**：Heartbeat 已由 gateway/cron 体系驱动。
- **v0.2.2 可用**：WebUI 可展示和管理绑定会话的定时自动化。

这些能力已经足够支撑稳定版教程里的定时任务与后台检查，不需要 main 的本地触发器。

### 仅 main/未来版本

- **仅 main/未来版本**：聊天中的 `/trigger <name>` 创建会话绑定的本地触发器。
- **仅 main/未来版本**：本地脚本可用 `nanobot trigger <id> <message>` 投递消息。
- **仅 main/未来版本**：投递写入工作区的持久队列；目标会话忙碌时，由自动化轮次协调器延后处理。

这里列出命令只为辨识版本差异，不是让 v0.2.2 用户执行。固定源码入口：[`session_automations.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/webui/session_automations.py)、[`AutomationTurnCoordinator`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/automation_turns.py)、[`LocalTriggerStore`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/triggers/local_store.py)。

## Goals 与 Subagents

### v0.2.2 可用

- **v0.2.2 可用**：持续 Goal 会保存在会话元数据中，并跨普通 Agent 轮次继续推进。
- **v0.2.2 可用**：稳定版的 Goal 工具采用 `long_task` / `complete_goal` 生命周期。
- **v0.2.2 可用**：`SubagentManager` 与 `spawn` 工具已经存在；“有 Subagents”本身不是 main 差异。

### 仅 main/未来版本

- **仅 main/未来版本**：Goal 工具改为 `create_goal` 与 `update_goal`，后者显式区分完成、取消、阻塞和替换。
- **仅 main/未来版本**：Goal 变更增加用户显式请求与运行时授权边界，避免模型自行扩大持续任务。
- **仅 main/未来版本**：这些工具名和授权语义不能用于推断 v0.2.2 的命令或工具接口。

固定源码入口：[`long_task.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/tools/long_task.py)、[`goal_permission.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/goal_permission.py)、[`subagent.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/subagent.py)。

## MCP

### v0.2.2 可用

- **v0.2.2 可用**：MCP 客户端支持 stdio、SSE 与 Streamable HTTP。
- **v0.2.2 可用**：远端 tool、resource 和 prompt 都可以包装为 nanobot Tool。
- **v0.2.2 可用**：超时、断线重连与配置热重载已经存在，不应统称为 main 新功能。

### 仅 main/未来版本

- **仅 main/未来版本**：固定快照进一步加固远程 URL 解析与连接目标固定，降低重绑定类 SSRF 风险。
- **仅 main/未来版本**：日志中的 MCP URL 会移除凭据、查询参数和片段。
- **仅 main/未来版本**：MCP 图像结果保存为本地产物，避免把大段 base64 直接放入模型上下文。
- **仅 main/未来版本**：当 `enabledTools` 不是通配允许时，不注册缺少等价白名单的 resource/prompt。

这些变化是纵深防御，不应被表述为“v0.2.2 没有 MCP”。固定源码入口：[`agent/tools/mcp.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/agent/tools/mcp.py)。

## Channel 插件架构

### v0.2.2 可用

- **v0.2.2 可用**：内置 Channel 是 `nanobot/channels/*.py` 形式的扁平模块。
- **v0.2.2 可用**：第三方包可通过 `nanobot.channels` entry-point group 注册 Channel。
- **v0.2.2 可用**：若外部插件与内置 Channel 同名，内置实现优先。

### 仅 main/未来版本

- **仅 main/未来版本**：内置 Channel 迁移为 `nanobot/channels/<name>/` 自包含包。
- **仅 main/未来版本**：每个包可通过 `manifest.py` 声明无重依赖的描述信息，并把 runtime、连接、校验、测试和 WebUI 资源放在同一边界内。
- **仅 main/未来版本**：固定快照会检测旧 `nanobot.channels` entry point，但只打印迁移警告，不加载它。

!!! danger "不要误读“插件化”"

    main 的 `ChannelPlugin` 描述的是仓库内自包含 Channel 包契约。它不等于继续支持 v0.2.2 的第三方 entry-point 加载方式。为稳定版编写外部 Channel 时，应继续遵循 v0.2.2 接口；评估 main 时则需要单独设计迁移。

固定源码入口：[`registry.py`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/channels/registry.py)、[`ChannelPlugin`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/channels/plugin.py)、[`Channel contracts`](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/channels/contracts.py)、[Telegram manifest](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/channels/telegram/manifest.py)、[Telegram runtime](https://github.com/HKUDS/nanobot/blob/b189a37648e4fa64f662b15de4f78ffd0bab403b/nanobot/channels/telegram/runtime.py)。

## 阅读与升级规则

1. **v0.2.2 可用** 的能力，按教程正文中的稳定版命令和配置操作。
2. **仅 main/未来版本** 的能力，只用于理解架构方向；不要复制到稳定环境。
3. 同名概念不代表接口不变。尤其要重新核对 Bootstrap 归属、Goal 工具名和 Channel 加载契约。
4. 所有 main 源码链接都固定到 `b189a37648e4fa64f662b15de4f78ffd0bab403b`；不要用分支 URL 替换。
5. 升级到后续稳定版时，重新执行维护清单，再决定哪些差异可以移入正文。

继续阅读：[首页的版本基线](../../index.md)、[阅读指南](../README.md)、[术语表](glossary.md)、[统一排障手册](troubleshooting-guide.md)。
