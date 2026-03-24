# 第 4 章：先部署到 Telegram

> 目标：先把你的 Bot 接到 Telegram，让它在真实聊天场景中工作；再理解为什么 nanobot 能继续扩展到其他平台。

## 4.1 从 CLI 到 Gateway

前三章我们一直用 `nanobot agent` 在终端里聊天。现在先选一个最容易上手的平台，把 Bot 真正放进聊天场景里。

关键区别：

| | CLI 模式 | Gateway 模式 |
|---|---|---|
| 命令 | `nanobot agent` | `nanobot gateway` |
| 用户界面 | 终端 | Telegram / 其他聊天平台 |
| 运行方式 | 聊完就退出 | 持续运行，等待消息 |
| 消息来源 | 键盘输入 | 聊天平台 API |

## 4.2 实操：连接 Telegram

Telegram 是最容易上手的平台。

### 第一步：创建 Telegram Bot

1. 在 Telegram 里搜索 `@BotFather`
2. 发送 `/newbot`，按提示设置名字
3. 复制得到的 Bot Token（格式类似 `123456:ABC-DEF...`）

### 第二步：配置

编辑 `~/.nanobot/config.json`，添加 Telegram 配置：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-你的密钥"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "你的Bot Token",
      "allowFrom": ["你的Telegram用户ID"]
    }
  }
}
```

> `allowFrom` 是安全白名单。**空数组 `[]` 会拒绝所有人**，设为 `["*"]` 允许任何人。
> 你的用户 ID 可以在 Telegram 设置中查看，格式如 `@yourUserId`，配置时**去掉 `@`**。

### 第三步：启动

```bash
nanobot gateway
```

输出：
```
🐈 Starting nanobot gateway on port 18790...
✓ Channels enabled: telegram
✓ Heartbeat: every 1800s
```

现在打开 Telegram，给你的 Bot 发消息，它就会回复了。

如果没有回复，先不要急着改代码，按下面顺序排查：

1. `nanobot gateway` 是否持续运行，没有直接退出
2. 日志里是否显示 `Channels enabled: telegram`
3. `allowFrom` 是否真的包含你的 Telegram 用户 ID
4. Bot Token 是否来自正确的 Bot，而不是旧 token

## 4.3 为什么先从 Telegram 开始

Telegram 是最适合做第一站的平台：

1. 配置最少，只需要 Bot Token
2. 调试路径短，`gateway` 启动后就能立即发消息验证
3. 跑通 Telegram 后，再理解 Discord、Slack、飞书等平台的接入方式会轻松很多

这一章只手把手带你完成 Telegram。其他平台的共性原理和配置形态，放在下面做总览。

## 4.4 其他平台

每个平台的配置方式类似——在 `channels` 中启用对应平台并填入凭据：

| 平台 | 关键配置 | 连接方式 |
|------|---------|---------|
| Telegram | Bot Token | 长轮询 |
| Discord | Bot Token | WebSocket |
| Slack | Bot Token + App Token | Socket Mode |
| 飞书 | App ID + App Secret | WebSocket |
| 钉钉 | Client ID + Client Secret | Stream Mode |
| WhatsApp | QR 码扫描 | WebSocket Bridge |
| QQ | App ID + App Secret | WebSocket |
| Email | IMAP/SMTP 凭据 | 轮询 |
| Matrix | Access Token | 长连接 |

多个平台可以同时启用——一个 `nanobot gateway` 进程就能同时服务所有平台。

## 4.5 多实例部署

如果你想运行多个不同的 Bot（比如一个 Telegram 财务顾问 + 一个 Discord 编程助手），可以用 `--config` 隔离：

```bash
# 实例 A：Telegram 财务顾问
nanobot gateway --config ~/.nanobot-finance/config.json

# 实例 B：Discord 编程助手
nanobot gateway --config ~/.nanobot-coder/config.json
```

每个实例有独立的配置、工作区、记忆和技能。

---

## 原理：消息总线架构

nanobot 能同时支持这么多平台，核心设计是**消息总线（MessageBus）**。

### 整体架构

```
 Telegram ─┐                          ┌─ Telegram
 Discord ──┤  InboundMessage           │  OutboundMessage
 Slack ────┤──────────────→ MessageBus ────────────────→ Slack
 Email ────┤                    │      │              Email
 CLI ──────┘                    ↓      └── CLI
                           AgentLoop
                          (统一处理)
```

所有平台的消息都被转换成统一的 `InboundMessage` 格式，通过 MessageBus 传给 AgentLoop。AgentLoop 不关心消息来自哪个平台——它只处理文本，返回 `OutboundMessage`，再由 MessageBus 路由到正确的平台。

### 消息格式

```python
# nanobot/bus/events.py

class InboundMessage:
    channel: str      # "telegram", "discord", "cli", ...
    sender_id: str    # 发送者 ID
    chat_id: str      # 会话 ID
    content: str      # 消息内容
    media: list[str]  # 附件路径（图片等）
    metadata: dict    # 平台附加字段

class OutboundMessage:
    channel: str      # 发回哪个平台
    chat_id: str      # 发到哪个会话
    content: str      # 回复内容
    reply_to: str|None# 可选：回复某条消息
```

### MessageBus 的实现

MessageBus 的核心就是两组方法（`nanobot/bus/queue.py`）：

```python
class MessageBus:
    async def publish_inbound(self, message: InboundMessage):
        """Channel 收到消息 → 放入队列"""

    async def consume_inbound(self) -> InboundMessage:
        """AgentLoop 取出消息 → 处理"""

    async def publish_outbound(self, message: OutboundMessage):
        """AgentLoop 发出回复 → 放入队列"""

    async def consume_outbound(self) -> OutboundMessage:
        """Channel 取出回复 → 发送到平台"""
```

整个 MessageBus 代码量很小，但实现了完全的解耦——Channel 和 Agent 互不依赖。

### 为什么这么设计？

1. **加新平台零成本**：添加一个新 Channel 只需要实现"收消息 → InboundMessage"和"OutboundMessage → 发消息"的转换，不需要改 Agent 的一行代码
2. **统一处理**：不管消息来自 Telegram 还是 Email，Agent 的处理逻辑完全一样
3. **天然支持多平台**：同一个 Agent 可以同时服务 Telegram + Discord + Slack，因为它根本不关心消息来源

### Gateway 的启动流程

当执行 `nanobot gateway` 时，可以从 `nanobot/cli/commands.py` 的 `gateway` 命令入口往下读：

```python
# 1. 加载配置
config = _load_runtime_config(config, workspace)

# 2. 创建核心组件
bus = MessageBus()                    # 消息总线
provider = _make_provider(config)     # LLM Provider
agent = AgentLoop(bus=bus, ...)       # Agent 引擎

# 3. 创建 Channel 管理器（根据配置启用对应平台）
channels = ChannelManager(config, bus)

# 4. 创建附加服务
cron = CronService(...)               # 定时任务
heartbeat = HeartbeatService(...)     # 心跳任务

# 5. 并行运行
await asyncio.gather(
    agent.run(),            # Agent 持续监听消息
    channels.start_all(),   # 所有 Channel 持续收发消息
)
```

### Session 会话管理

nanobot 用 `session_key`（格式：`channel:chat_id`）来区分不同的对话。比如：
- `telegram:123456` — Telegram 上 ID 为 123456 的用户的对话
- `discord:789012` — Discord 上 ID 为 789012 的用户的对话
- `cli:direct` — 命令行直接对话

每个 session 有独立的对话历史，互不干扰。

## 4.6 安全配置

部署到公网后，安全很重要：

### allowFrom：访问白名单

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "...",
      "allowFrom": ["123456789"]
    }
  }
}
```

- `[]`（空数组）：**拒绝所有人**（默认，最安全）
- `["123456789"]`：只允许指定用户
- `["*"]`：允许所有人（谨慎使用）

### restrictToWorkspace：沙箱模式

```json
{
  "tools": {
    "restrictToWorkspace": true
  }
}
```

设为 `true` 后，Bot 的所有文件操作和 shell 命令都被限制在工作区内，无法访问系统其他目录。**生产环境强烈建议开启。**

## 4.7 后台运行

#### 使用 systemd（Linux 推荐）

创建 `~/.config/systemd/user/nanobot-gateway.service`：

```ini
[Unit]
Description=Nanobot Gateway
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/nanobot gateway
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

启动：

```bash
systemctl --user daemon-reload
systemctl --user enable --now nanobot-gateway
```

查看日志：

```bash
journalctl --user -u nanobot-gateway -f
```

#### 使用 Docker

```bash
docker build -t nanobot .
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 nanobot gateway
```

## 4.8 验证与排障

部署成功后，至少确认下面几项：

1. gateway 进程持续存活
2. 日志里能看到启用的 channel
3. 从目标平台发消息后，能看到 inbound 处理痕迹或回复结果
4. 会话目录中开始出现对应 session 文件

常见问题：

- 进程一启动就退出：通常是配置缺失、token 错误或 provider 初始化失败
- Bot 在线但不回复：先检查 `allowFrom`、平台回调权限和日志报错
- 回复串台：检查 `chat_id` / `session_key` 的隔离逻辑，而不是只看最终文本
- Docker 中能启动但平台不可达：通常是挂载配置没进去，或容器内缺少本地依赖

---

## 总结：你的 Bot 全貌

经过前四章的学习，你已经理解了 nanobot 的完整架构：

```
config.json
    │
    ├── providers（LLM 连接）
    │       ↓
    ├── AgentLoop（核心引擎）
    │       ├── ContextBuilder → System Prompt
    │       │       ├── Identity（固定身份）
    │       │       ├── SOUL.md（你定义的性格）
    │       │       ├── AGENTS.md（你定义的规则）
    │       │       ├── USER.md（用户画像）
    │       │       ├── TOOLS.md（工具约束）
    │       │       ├── memory/MEMORY.md（长期记忆）
    │       │       └── skills/（技能摘要）
    │       ├── ToolRegistry → 工具集
    │       │       ├── exec（执行命令）
    │       │       ├── read_file / write_file / edit_file（文件操作）
    │       │       ├── web_search / web_fetch（网络）
    │       │       ├── message（发消息）
    │       │       ├── spawn（子任务）
    │       │       └── cron（定时任务）
    │       └── SessionManager → 会话隔离
    │
    ├── MessageBus（消息总线）
    │       ↓
    └── Channels（聊天平台）
            ├── Telegram
            ├── Discord
            ├── Slack
            └── ...
```

你定制的每一部分都对应架构中的一个模块：

| 你做的事 | 对应的模块 |
|---------|-----------|
| 改 config.json | providers / channels |
| 改 SOUL.md / AGENTS.md | ContextBuilder |
| 创建 Skill | SkillsLoader |
| 编辑 MEMORY.md | MemoryStore |

核心代码只有约 4,280 行，却实现了一个功能完备的 AI Agent。这就是 nanobot "超轻量"的含义——不是功能少，而是设计精炼。

下一章我们不再新增概念，而是把前四章真正串起来，做出一个从配置、定制、扩展到 Telegram 上线都完整闭环的 Bot。

---

[← 上一章：教 Bot 新技能](03-skills.md) | [下一章：做一个真实可用的 Bot →](05-first-real-bot.md) | [回到目录](README.md)
