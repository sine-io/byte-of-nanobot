# 第 1 章：5 分钟跑起来

> 目标：安装 nanobot，配置 API Key，完成第一次对话。

## 1.1 安装

三种方式任选其一：

```bash
# 方式 A：从源码安装（推荐，能看到代码）
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
pip install -e .

# 方式 B：用 uv 安装（快）
uv tool install nanobot-ai

# 方式 C：用 pip 安装
pip install nanobot-ai
```

验证安装：

```bash
nanobot --version
# 输出类似：🐈 nanobot v0.x.y
```

如果命令不存在，先检查两件事：

- 你是否把安装目录加入了 `PATH`
- 你当前使用的 `python` / `pip` / `uv` 是否属于同一个环境

## 1.2 初始化

```bash
nanobot onboard
```

这条命令做了三件事：

1. 在 `~/.nanobot/config.json` 生成默认配置
2. 在 `~/.nanobot/workspace/` 创建工作区
3. 从模板同步必要文件（SOUL.md、AGENTS.md 等）

运行后，你会看到：

```
✓ Created config at ~/.nanobot/config.json
✓ Created workspace at ~/.nanobot/workspace

🐈 nanobot is ready!

Next steps:
  1. Add your API key to ~/.nanobot/config.json
  2. Chat: nanobot agent -m "Hello!"
```

## 1.3 配置 API Key

编辑 `~/.nanobot/config.json`，填入你的 API Key。以 OpenRouter 为例：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-你的密钥"
    }
  },
  "agents": {
    "defaults": {
      "model": "your-provider-supported-model"
    }
  }
}
```

> **其他 Provider 也可以。** nanobot 支持多种 LLM 提供商（OpenAI、Anthropic、DeepSeek、Gemini 等）。
> 只需在 `providers` 里填对应的 key，在 `model` 里写当前 provider 支持、且你账号可用的模型名即可。

## 1.4 第一次对话

```bash
# 单条消息模式
nanobot agent -m "你好，请介绍一下你自己"

# 交互模式（推荐）
nanobot agent
```

交互模式下，输入 `exit` 或按 `Ctrl+C` 退出。

## 1.5 验证与排障

完成前四步后，至少确认下面 4 项：

1. `nanobot --version` 能正常输出版本号
2. `~/.nanobot/config.json` 已存在，且 provider key 已填写
3. `~/.nanobot/workspace/` 已创建，里面至少有 `AGENTS.md` 和 `SOUL.md`
4. 运行 `nanobot agent -m "你好"` 时，不会报配置错误或鉴权错误

常见问题：

- 报 `401` / `Unauthorized`：通常是 API Key 不对，或 provider 与 model 不匹配
- 报模型不存在：先确认 `model` 名称是否是当前 provider 支持的格式
- 报命令不存在：通常是 `nanobot` 没装到当前 shell 环境，重新检查安装方式和 `PATH`
- `onboard` 后没有工作区：检查当前用户对 `~/.nanobot/` 是否有写权限

---

## 原理：nanobot 是怎么跑起来的？

当你执行 `nanobot agent` 时，背后发生了什么？可以用三段来概括：

```
config.json ──→ Provider（连接 LLM）──→ AgentLoop（收发消息、调用工具）
```

对应源码可以从 `nanobot/cli/commands.py` 中的 `agent` 命令入口开始看：

```python
# 第一步：加载配置
config = _load_runtime_config(config, workspace)

# 第二步：创建 Provider（负责和 LLM API 通信）
provider = _make_provider(config)

# 第三步：创建 AgentLoop（核心处理引擎）
agent_loop = AgentLoop(
    bus=bus,
    provider=provider,
    workspace=config.workspace_path,
    model=config.agents.defaults.model,
    ...
)
```

### Provider 是什么？

Provider 是 nanobot 和 LLM 之间的桥梁。它负责把你的消息发给 LLM，再把 LLM 的回复拿回来。

nanobot 用了一个叫 LiteLLM 的库来统一不同 LLM 的 API 差异。不管你用 OpenAI、Anthropic 还是 DeepSeek，Provider 都帮你处理好了格式转换——你只需要换 `model` 和 `apiKey`。

### AgentLoop 是什么？

AgentLoop 是 nanobot 的"大脑"，它按照这个循环工作（可从 `nanobot/agent/loop.py` 中的主循环逻辑继续追）：

```
     ┌──────────────────────────────┐
     │  1. 组装上下文（System Prompt │
     │     + 历史消息 + 当前消息）    │
     │              ↓                │
     │  2. 调用 LLM                  │
     │              ↓                │
     │  3. LLM 返回了什么？           │
     │     ├── 纯文本 → 返回给用户    │
     │     └── 工具调用 → 执行工具    │
     │              ↓                │
     │  4. 把工具结果反馈给 LLM       │
     │              ↓                │
     │         回到第 2 步            │
     └──────────────────────────────┘
```

这就是经典的 **ReAct 循环**（Reasoning + Acting）：LLM 思考 → 调用工具 → 观察结果 → 再思考，直到给出最终回答。默认最多循环 40 次（`max_iterations=40`）。

### 工作区 (Workspace) 是什么？

工作区是 Bot 的"家"，默认在 `~/.nanobot/workspace/`。初始化后的结构：

```
workspace/
├── AGENTS.md     ← Bot 的行为指令
├── SOUL.md       ← Bot 的人格
├── USER.md       ← 用户画像
├── TOOLS.md      ← 工具使用说明
├── HEARTBEAT.md  ← 周期性任务
├── memory/
│   ├── MEMORY.md ← 长期记忆（每次对话都会读取）
│   └── HISTORY.md← 历史日志（可搜索）
└── skills/       ← 自定义技能目录
```

这些文件会被注入到 LLM 的 System Prompt 中。**修改它们就能改变 Bot 的行为——不需要写代码。**

这里有一个理解上的简化：文档先讲主干机制，实际实现里还会附带运行时信息、平台策略和技能摘要等内容。第一次阅读时先抓住主线就够了，后面章节再补细节。

下一章我们就来做这件事。

---

[下一章：用 Markdown 定义 Bot →](02-soul.md)
