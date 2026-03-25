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

### 接平台前，先确认这 3 件事

在继续之前，先停 30 秒确认：

1. 你已经能用 `nanobot agent -m "你好"` 在 CLI 中拿到正常回复
2. 你改过 `SOUL.md` 或 `AGENTS.md`，并观察到回复确实发生变化
3. 你至少让一个 Skill 成功触发过一次

如果这 3 条还没成立，建议先回到前 3 章。否则你接下来一旦收不到 Telegram 回复，会很难判断问题到底出在平台、配置还是 Bot 本身。

### 第一步：创建 Telegram Bot

1. 在 Telegram 里搜索 `@BotFather`
2. 发送 `/newbot`，按提示设置名字
3. 复制得到的 Bot Token（格式类似 `123456:ABC-DEF...`）

### 第二步：找到你的 Telegram 数字用户 ID

`allowFrom` 需要的不是用户名，而是你的 **数字用户 ID**。最简单的取法通常有两种：

1. 直接给一些常见的 Telegram ID 查询机器人发消息，读取它返回的数字 ID
2. 暂时把 `allowFrom` 设成 `["*"]` 做一次本地验证，从日志或调试输出中拿到你的发送者 ID，再立刻改回只允许自己

无论哪种方式，最终都应该拿到类似 `123456789` 这样的纯数字字符串。

### 第三步：配置

在第 1 章已经可用的 `~/.nanobot/config.json` 基础上，至少补齐下面两段；如果 provider 或 model 还没配好，先回到第 1 章完成：

```json
{
  "tools": {
    "restrictToWorkspace": true
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "你的Bot Token",
      "allowFrom": ["你的Telegram数字用户ID"]
    }
  }
}
```

> 第一次上线前，先确认两件事：`allowFrom` 先只放你自己的 **Telegram 数字用户 ID**；`tools.restrictToWorkspace` 先设为 `true`。
> `allowFrom` 是安全白名单。**空数组 `[]` 会拒绝所有人**，设为 `["*"]` 允许任何人。这里要填的是类似 `123456789` 这样的数字 ID，不是用户名，也不带 `@`。

#### 最容易配错的字段：`allowFrom`

第一次接 Telegram，最常见的误区不是 token，而是 `allowFrom`：

- 填 `@username`：错，应该填数字 ID
- 填空数组 `[]`：这会拒绝所有人
- 长时间保留 `["*"]`：可以临时调试，不建议长期这么放
- 以为“Bot 在线但不回复”一定是 gateway 坏了：很多时候只是白名单没放行

所以第一次最稳的配置是：

```json
"allowFrom": ["你的Telegram数字用户ID"]
```

### 第四步：启动

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
3. `allowFrom` 是否真的包含你的 Telegram 数字用户 ID
4. Bot Token 是否来自正确的 Bot，而不是旧 token
5. provider 和 model 是否本来就在 CLI 模式下可用

第一次部署时，建议**先用前台运行的 `nanobot gateway` 调通**，不要一开始就放进 `systemd` 或 Docker。先把“能不能收到消息并回复”这条最短链路跑通，再做后台运行。

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

### restrictToWorkspace：沙箱模式

```json
{
  "tools": {
    "restrictToWorkspace": true
  }
}
```

设为 `true` 后，Bot 的所有文件操作和 shell 命令都被限制在工作区内，无法访问系统其他目录。**生产环境强烈建议开启。**

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
- 这里的值是 Telegram 的**数字用户 ID**，不是 `@username`

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

如果你想快速缩小范围，最有效的顺序是：

1. 先确认 CLI 模式本来就能回复
2. 再确认 `gateway` 进程持续存活
3. 再确认 Telegram channel 已启用
4. 再确认 `allowFrom` 放行了你自己
5. 最后才去怀疑平台侧或 Docker/systemd

如果你已经分不清问题是在 CLI、Skill、provider，还是 Telegram 这一层，先回到[附录：常见坑与排障](appendix-troubleshooting.md)按分层方式排查。

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

核心实现规模依然相当克制，却实现了一个功能完备的 AI Agent。这就是 nanobot "超轻量"的含义——不是功能少，而是设计精炼。

下一章我们不再新增概念，而是把前四章真正串起来，做出一个从配置、定制、扩展到 Telegram 上线都完整闭环的 Bot。
