# 第 4 章：消息总线

> 解耦 Agent 和 I/O，让同一个 Agent 同时服务终端、Telegram、Discord。

## 问题

前三章的代码是这样的：

```python
user_input = input("You: ")     # 写死了：只能从终端读
reply = await agent_loop(...)
print(f"Bot: {reply}")           # 写死了：只能往终端写
```

如果想接入 Telegram，就得在 Agent 核心代码里加 Telegram 的逻辑。接入 Discord 再加一份。代码会变成一团意大利面。

nanobot 的解法：**消息总线（MessageBus）**——只有 45 行代码，但彻底解耦了 Agent 和 I/O。

## 核心设计

```
Terminal ──┐                           ┌── Terminal
Telegram ──┤  InboundMessage           │   OutboundMessage
Discord ───┤──────────────→ MessageBus ────────────────→ Discord
           │                    │      │
           └────────────────    ↓      └── Telegram
                            AgentLoop
                           (不关心消息来自哪里)
```

Agent 只和 MessageBus 打交道，不知道也不关心消息是从 Telegram 还是终端来的。

## 第一步：定义消息类型

对应 `nanobot/bus/events.py`（38 行）：

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class InboundMessage:
    """从外部收到的消息"""
    channel: str         # "cli", "telegram", "discord"
    sender_id: str       # 发送者 ID
    chat_id: str         # 会话 ID
    content: str         # 消息正文

    @property
    def session_key(self) -> str:
        return f"{self.channel}:{self.chat_id}"

@dataclass
class OutboundMessage:
    """要发出去的消息"""
    channel: str
    chat_id: str
    content: str
```

关键字段是 `channel`——它告诉系统"这条消息来自哪个平台"和"应该发回哪个平台"。

## 第二步：MessageBus

对应 `nanobot/bus/queue.py`（45 行），nanobot 中最精简的模块：

```python
import asyncio

class MessageBus:
    """异步消息总线——对应 nanobot/bus/queue.py"""

    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, msg: InboundMessage):
        await self.inbound.put(msg)

    async def consume_inbound(self) -> InboundMessage:
        return await self.inbound.get()

    async def publish_outbound(self, msg: OutboundMessage):
        await self.outbound.put(msg)

    async def consume_outbound(self) -> OutboundMessage:
        return await self.outbound.get()
```

就是两个 `asyncio.Queue`。一个进、一个出。简单到不能再简单。

### 为什么用队列而不是直接调用？

因为**解耦**。Channel 不需要知道 Agent 的存在，Agent 也不需要知道 Channel 的存在。它们只需要知道 MessageBus：

- Channel：收到消息 → `bus.publish_inbound()`
- Agent：`bus.consume_inbound()` → 处理 → `bus.publish_outbound()`
- Channel：`bus.consume_outbound()` → 发送

新增一个 Channel 不需要改 Agent 的一行代码。

## 第三步：Channel 基类

对应 `nanobot/channels/base.py`（117 行）：

```python
from abc import ABC, abstractmethod

class BaseChannel(ABC):
    """聊天平台的抽象基类——对应 nanobot/channels/base.py"""

    name: str = "base"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @abstractmethod
    async def start(self):
        """连接平台，开始监听消息"""
        ...

    @abstractmethod
    async def stop(self):
        """断开连接"""
        ...

    @abstractmethod
    async def send(self, msg: OutboundMessage):
        """发送消息到平台"""
        ...

    async def handle_message(self, sender_id: str, chat_id: str, content: str):
        """收到消息时调用——转发到 Bus"""
        await self.bus.publish_inbound(InboundMessage(
            channel=self.name, sender_id=sender_id,
            chat_id=chat_id, content=content,
        ))
```

每个具体平台只需要实现三个方法：`start`（连接）、`stop`（断开）、`send`（发送）。

## 第四步：实现 CLI Channel

最简单的 Channel——从终端读写：

```python
class CLIChannel(BaseChannel):
    """终端 Channel"""
    name = "cli"

    async def start(self):
        """在独立的线程中读取终端输入"""
        loop = asyncio.get_event_loop()
        while True:
            user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            await self.handle_message("user", "direct", user_input)

    async def stop(self):
        pass

    async def send(self, msg: OutboundMessage):
        print(f"\nBot: {msg.content}\n")
```

## 第五步：实现 Telegram Channel

用 `python-telegram-bot` 库（`pip install python-telegram-bot`）：

```python
class TelegramChannel(BaseChannel):
    """Telegram Channel——对应 nanobot/channels/telegram.py（简化版）"""
    name = "telegram"

    def __init__(self, bus: MessageBus, token: str, allow_from: list[str]):
        super().__init__(bus)
        self.token = token
        self.allow_from = allow_from
        self._app = None

    async def start(self):
        from telegram import Update
        from telegram.ext import ApplicationBuilder, MessageHandler, filters

        self._app = ApplicationBuilder().token(self.token).build()

        async def on_message(update: Update, context):
            msg = update.effective_message
            if not msg or not msg.text:
                return
            sender = str(update.effective_user.id)
            if self.allow_from and "*" not in self.allow_from:
                if sender not in self.allow_from:
                    return  # 不在白名单中
            await self.handle_message(sender, str(msg.chat_id), msg.text)

        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()

    async def stop(self):
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    async def send(self, msg: OutboundMessage):
        if self._app:
            await self._app.bot.send_message(chat_id=msg.chat_id, text=msg.content)
```

**注意对比**：CLI Channel 和 Telegram Channel 实现了**完全相同的接口**。Agent 看到的只是 `InboundMessage` 和 `OutboundMessage`，根本不知道消息是从终端还是 Telegram 来的。

## 第六步：改造 AgentLoop

把前三章的 `main()` 函数改造成基于 Bus 的 AgentLoop：

```python
class AgentLoop:
    """基于消息总线的 Agent 循环——对应 nanobot/agent/loop.py"""

    def __init__(self, bus: MessageBus, tools: ToolRegistry,
                 ctx: ContextBuilder, sessions: SessionManager):
        self.bus = bus
        self.tools = tools
        self.ctx = ctx
        self.sessions = sessions

    async def run(self):
        """持续监听并处理消息"""
        while True:
            try:
                msg = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            # 处理消息
            session = self.sessions.get_or_create(msg.session_key)
            history = session.get_history(max_messages=50)
            messages = self.ctx.build_messages(history, msg.content)

            reply = await self._react_loop(messages)

            # 保存到 session
            session.messages.append({"role": "user", "content": msg.content,
                                      "timestamp": datetime.now().isoformat()})
            session.messages.append({"role": "assistant", "content": reply,
                                      "timestamp": datetime.now().isoformat()})
            self.sessions.save(session)

            # 发回消息（通过 Bus）
            await self.bus.publish_outbound(OutboundMessage(
                channel=msg.channel, chat_id=msg.chat_id, content=reply,
            ))

    async def _react_loop(self, messages: list[dict]) -> str:
        for _ in range(10):
            resp = client.chat.completions.create(
                model=MODEL, messages=messages,
                tools=self.tools.get_definitions() or None, temperature=0.1,
            )
            m = resp.choices[0].message
            if m.tool_calls:
                messages.append({"role": "assistant", "content": m.content, "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in m.tool_calls
                ]})
                for tc in m.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = await self.tools.execute(tc.function.name, args)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return m.content or ""
        return "Max iterations reached."
```

## 第七步：消息路由

最后一个拼图——把 Agent 的回复路由到正确的 Channel：

```python
async def route_outbound(bus: MessageBus, channels: dict[str, BaseChannel]):
    """把 Agent 的回复路由到对应的 Channel"""
    while True:
        try:
            msg = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        ch = channels.get(msg.channel)
        if ch:
            await ch.send(msg)
```

## 完整的 Gateway 启动

```python
async def run_gateway():
    """启动 Gateway——对应 nanobot/cli/commands.py 的 gateway 命令"""
    init_workspace()
    bus = MessageBus()

    # 注册工具
    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    ctx = ContextBuilder(WORKSPACE)
    sessions = SessionManager(WORKSPACE)
    agent = AgentLoop(bus, tools, ctx, sessions)

    # 启用 Channels
    channels: dict[str, BaseChannel] = {}
    channels["cli"] = CLIChannel(bus)
    # channels["telegram"] = TelegramChannel(bus, token="YOUR_TOKEN", allow_from=["*"])

    print(f"Gateway started. Channels: {list(channels.keys())}\n")

    # 并行运行所有组件
    await asyncio.gather(
        agent.run(),
        route_outbound(bus, channels),
        *[ch.start() for ch in channels.values()],
    )

if __name__ == "__main__":
    asyncio.run(run_gateway())
```

## 架构图

```
┌─────────┐     publish_inbound     ┌────────────┐
│  CLI    ├─────────────────────────→│            │  consume_inbound
│ Channel │                          │  MessageBus │←──────────────── AgentLoop
└─────────┘     consume_outbound     │            │  publish_outbound     │
┌─────────┐←────────────────────────│            │←──────────────────────┘
│Telegram │                          └────────────┘
│ Channel │  (route_outbound 负责
└─────────┘   根据 msg.channel 分发)
```

## 关键对比

| 概念 | 我们的代码 | nanobot |
|------|-----------|---------|
| MessageBus | 2 个 asyncio.Queue | 完全相同 (`bus/queue.py`, 45 行) |
| InboundMessage | 4 个字段 | 同 + media, metadata, session_key_override |
| BaseChannel | 3 个抽象方法 | 同 + is_allowed 白名单检查 |
| AgentLoop.run | 消费消息 → 处理 → 发回 | 同 + 任务调度 + /stop 取消 + 并发锁 |
| 消息路由 | 单独的 route_outbound | 集成在 ChannelManager 中 |

## 还缺什么？

Agent 现在可以同时服务多个平台了。但它的能力是固定的——只有 exec、read_file、write_file 三个工具。

如果用户想让它查天气、操作 GitHub、定时提醒呢？下一章：技能系统——让 Agent 能力可以动态扩展。

## 本章你真正学到的抽象

这一章的关键不是 Telegram 接入代码，而是“Agent 核心不直接依赖任何 I/O 平台”这个边界设计：

- `InboundMessage` / `OutboundMessage` 统一了消息格式
- `MessageBus` 统一了流转通道
- `Channel` 只负责平台适配，不负责推理逻辑

这是系统从“单脚本应用”升级成“可扩展服务”的分界线。

## 最小验证步骤

最少做下面 4 步：

1. 只启用 `CLIChannel`，确认通过总线仍然能完成一次完整对话
2. 打印或观察 `msg.channel`，确认回复会路由回正确的 channel
3. 同时启用两个 channel 时，确认不会把 A 平台的回复发到 B 平台
4. 重启 gateway 后再次发消息，确认 session 仍按 `channel:chat_id` 隔离

## 常见失败点

- 看起来“没回复”：很多时候不是 Agent 没处理，而是 outbound 路由没有跑起来
- 会话串台：通常是 `session_key` 设计不对，或多个平台复用了同一个 chat_id 而没有带 channel 前缀
- Channel 代码越来越重：说明平台适配层混进了业务逻辑，边界开始失守
- Telegram 能收不能发：通常是 send 路径和 inbound 路径只实现了一半，或者平台 SDK 生命周期管理有问题

---

[← 上一章：记忆与上下文](03-memory-and-context.md) | [下一章：技能与扩展 →](05-skills-and-beyond.md)
