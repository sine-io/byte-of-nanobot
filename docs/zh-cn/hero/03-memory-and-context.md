# 第 3 章：记忆与上下文

> 让 Agent 有记忆、有个性、能管理上下文窗口。

## 这一章一次解决 3 个问题

如果你觉得这一章信息量突然变大，这是正常的。因为它不是只补一个点，而是同时补齐了 3 个在上一章已经暴露出来的缺口：

- 对话重启后会失忆
- system prompt 太薄，Bot 没有稳定个性
- 历史消息会不断增长，最终撑爆上下文窗口

所以读这一章时，最好始终问自己：**当前这一段代码是在解决“记不住”、 “不像自己”，还是“放不下”这三个问题里的哪一个？**

## 三个问题

上一章的 Agent 有三个硬伤：

1. **没有持久记忆**——重启后什么都不记得
2. **没有个性**——system prompt 就一句话
3. **上下文会爆**——对话越长，messages 越大，最终超出 LLM 窗口

nanobot 用三个机制解决这些问题：**Session 持久化**、**Context Builder**、**Memory / Dream 整合**。

## 第一步：Session 持久化

对应 `nanobot/session/manager.py`。核心思路：每个对话存为一个 JSONL 文件，每行一条消息。

```python
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Session:
    """一次对话的所有状态——对应 nanobot/session/manager.py:17"""
    key: str
    messages: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_history(self, max_messages: int = 50) -> list[dict]:
        """取最近的 N 条消息，供 LLM 使用"""
        recent = self.messages[-max_messages:]
        # 确保从 user 消息开始（避免孤立的 tool_result）
        for i, m in enumerate(recent):
            if m.get("role") == "user":
                return recent[i:]
        return recent


class SessionManager:
    """管理多个会话的持久化——对应 nanobot/session/manager.py:73"""

    def __init__(self, data_dir: Path):
        self.dir = data_dir / "sessions"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        if key in self._cache:
            return self._cache[key]
        session = self._load(key) or Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session):
        path = self.dir / f"{session.key.replace(':', '_')}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for msg in session.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self._cache[session.key] = session

    def _load(self, key: str) -> Session | None:
        path = self.dir / f"{key.replace(':', '_')}.jsonl"
        if not path.exists():
            return None
        messages = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                messages.append(json.loads(line))
        return Session(key=key, messages=messages)
```

现在重启后对话历史不会丢了。nanobot 的实现还支持 metadata 行、legacy 路径迁移等，但核心就是 JSONL 持久化。

## 第二步：Context Builder——组装 System Prompt

这是 nanobot 最精巧的设计之一（`nanobot/agent/context.py`）。System Prompt 不是写死的，而是**动态组装**的：

```
System Prompt = 身份 + Bootstrap 文件 + 长期记忆 + 技能摘要 + 最近历史摘要
```

```python
class ContextBuilder:
    """组装 System Prompt——对应 nanobot/agent/context.py"""

    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def build_system_prompt(self) -> str:
        parts = [self._get_identity()]

        # 加载 Bootstrap 文件（用户可编辑的个性化文件）
        for filename in self.BOOTSTRAP_FILES:
            path = self.workspace / filename
            if path.exists():
                content = path.read_text(encoding="utf-8")
                parts.append(f"## {filename}\n\n{content}")

        # 加载长期记忆
        memory_file = self.workspace / "memory" / "MEMORY.md"
        if memory_file.exists():
            memory = memory_file.read_text(encoding="utf-8")
            if memory.strip():
                parts.append(f"# Memory\n\n{memory}")

        return "\n\n---\n\n".join(parts)

    def _get_identity(self) -> str:
        return f"""# Mini Agent

你是一个有帮助的 AI 助手。

## Workspace
工作区: {self.workspace}
长期记忆: {self.workspace}/memory/MEMORY.md

## Guidelines
- 先说意图，再调工具
- 修改文件前先读取
- 任务模糊时主动询问"""

    def build_messages(
        self, history: list[dict], user_message: str
    ) -> list[dict]:
        """组装完整的 messages 列表"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        runtime = f"[Runtime Context]\nCurrent Time: {now}"

        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": f"{runtime}\n\n{user_message}"},
        ]
```

### 为什么不把 system prompt 写死？

因为**用户要能定制 Bot 的行为**。通过 `SOUL.md` 改性格、`AGENTS.md` 改规则、`USER.md` 告诉 Bot 你是谁——全部是 Markdown 文件，改完下次对话自动生效。

`build_messages` 每次调用都重新读取这些文件，所以用户编辑后不需要重启。

## 第三步：持久化记忆

对应 `nanobot/agent/memory.py`。当前实现是分层设计：

| 层 | 文件 | 特点 |
|---|---|---|
| 长期记忆 | `memory/MEMORY.md` | **每次对话都注入** system prompt，存放重要事实 |
| 历史摘要归档 | `memory/history.jsonl` | 追加式 JSONL，可 grep / jq 搜索，存放被压缩后的旧对话 |
| Dream 状态 | `memory/.cursor` / `memory/.dream_cursor` | 记录摘要写入位置和 Dream 已处理位置 |
| 记忆版本 | `memory/.git/` | Dream 修改长期文件后的轻量版本历史 |

```python
class MemoryStore:
    """分层记忆——对应 nanobot/agent/memory.py（简化版）"""

    def __init__(self, workspace: Path):
        mem_dir = workspace / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = mem_dir / "MEMORY.md"
        self.history_file = mem_dir / "history.jsonl"
        self.cursor_file = mem_dir / ".cursor"

    def read_memory(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_memory(self, content: str):
        self.memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str):
        cursor = self._next_cursor()
        record = {
            "cursor": cursor,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": entry.rstrip(),
        }
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.cursor_file.write_text(str(cursor), encoding="utf-8")

    def _next_cursor(self) -> int:
        if self.cursor_file.exists():
            return int(self.cursor_file.read_text(encoding="utf-8").strip()) + 1
        return 1
```

### 记忆整合（Memory Consolidation）

当对话太长时，nanobot 会先由 **Consolidator** 把旧消息交给 LLM 总结，并把摘要追加到 `memory/history.jsonl`。随后 **Dream** 会定期读取这些新摘要，分析哪些内容应该沉淀为长期事实，再用文件工具谨慎编辑 `SOUL.md`、`USER.md` 和 `MEMORY.md`。

教学版为了让机制更容易看懂，把这两步压缩成一个 `consolidate_memory()`：旧消息 → 摘要 → `history.jsonl`，再把最重要的结论写入 `MEMORY.md`。真实 nanobot 的 token-driven consolidation 更克制：它主要推进内部游标，保留原始 session 文件，并只让未整合部分继续参与上下文构建。

这个机制确保了：
- 上下文窗口不会撑爆
- 重要信息不会丢失
- `MEMORY.md` 里的事实每次对话都可用

简化版实现：

```python
async def consolidate_memory(
    client: OpenAI, model: str,
    session: Session, memory: MemoryStore,
    keep_recent: int = 25,
):
    """把旧消息整合进记忆——教学版，对应 nanobot/agent/memory.py 的主干思想"""
    if len(session.messages) <= keep_recent:
        return  # 还不够长，不需要整合

    old = session.messages[:-keep_recent]
    current_memory = memory.read_memory()

    # 让 LLM 做总结
    prompt = f"""Summarize this conversation and update the memory.

## Current Memory
{current_memory or "(empty)"}

## Conversation
{json.dumps(old, ensure_ascii=False, indent=2)[:8000]}

Respond in JSON: {{"history": "summary for log", "memory": "updated memory markdown"}}"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You consolidate conversations into memory."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    try:
        result = json.loads(resp.choices[0].message.content)
        if result.get("history"):
            memory.append_history(result["history"])
        if result.get("memory"):
            memory.write_memory(result["memory"])
        # 教学简化：直接丢弃旧消息。真实 nanobot 更偏向推进游标并保留原始 session 文件。
        session.messages = session.messages[-keep_recent:]
        print("  [Memory] Consolidated old messages")
    except (json.JSONDecodeError, KeyError):
        pass  # 整合失败就跳过，不影响正常对话
```

nanobot 的实现更精巧：`Consolidator` 负责在上下文压力过大时把旧消息压缩进 `history.jsonl`；`Dream` 则作为后台记忆整理器，分两阶段分析历史摘要并编辑长期记忆文件。Dream 的修改还会进入轻量 Git 历史，用户可以用 `/dream-log` 和 `/dream-restore` 查看或恢复。

### 先别把这三个概念混在一起

| 概念 | 它解决什么 | 它存什么 |
|---|---|---|
| `Session` | 当前会话历史别丢 | 原始对话消息 |
| `Context Builder` | 每轮发给模型什么上下文 | system prompt + 历史 + 运行时信息 |
| `Memory` | 长对话里重要事实别丢 | 提炼后的长期事实和摘要 |

很多初学者会把“重启后还记得”和“长期记忆已经整合”混成一件事。实际上这是两层不同机制。

## 本章你真正学到的抽象

这一章真正引入了 3 个长期有效的设计点：

- `Session Persistence`：把对话状态从内存搬到磁盘
- `Context Builder`：把静态配置、动态记忆、运行时信息拼成统一上下文
- `Memory / Dream Consolidation`：用摘要归档和长期记忆对抗上下文窗口上限

从这里开始，Agent 不再只是“会调用工具的聊天循环”，而是一个有稳定人格、跨轮状态和上下文预算意识的系统。

## 最小验证步骤

建议按顺序做下面 4 个验证：

1. 跑一次程序并完成几轮对话，确认会生成 `sessions/` 和 `memory/` 相关文件
2. 重启程序，再问一个延续上一轮的问题，确认至少 session 历史仍然存在
3. 修改 `SOUL.md` 或 `AGENTS.md`，确认下一次对话的风格或流程发生变化
4. 构造一段较长对话，手动触发或观察记忆整合后 `memory/history.jsonl` 和 `MEMORY.md` 的变化；真实 nanobot 还可以用 `/dream-log` 查看 Dream 修改了什么

## 常见失败点

- 重启后“没有记忆”：先区分是 session 历史没保存，还是长期记忆没写入，这是两套机制
- 改了 `SOUL.md` 没效果：通常是 build_messages 没有重新读取文件，或 system prompt 没重新构建
- 记忆整合输出不稳定：让模型直接返回 JSON 很脆弱，真实 nanobot 把“压缩旧消息”和“整理长期记忆”拆成 Consolidator + Dream 两层来降低风险
- 上下文仍然爆掉：说明你只有“保存历史”，没有真正限制传给模型的历史窗口

## 完整代码

在看完整代码前，先记住本章新增的职责切分：

- `SessionManager`：负责把会话历史保存和读回来
- `ContextBuilder`：负责把静态文件、记忆和运行时信息拼成完整上下文
- `MemoryStore` / `consolidate_memory()`：负责把旧消息折叠成摘要归档和长期记忆

带着这 3 个问题去看代码，会比直接从头扫到尾轻松很多。

```python
"""mini_agent.py — 带记忆和个性的 Agent，~300 行"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

# ── 配置 ─────────────────────────────────────────────
API_BASE  = "https://openrouter.ai/api/v1"
API_KEY   = "sk-or-v1-你的密钥"
MODEL     = "your-provider-supported-model"
WORKSPACE = Path("~/.mini-agent/workspace").expanduser()

client = OpenAI(base_url=API_BASE, api_key=API_KEY)

# ── 初始化工作区 ─────────────────────────────────────
def init_workspace():
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "memory").mkdir(exist_ok=True)

    defaults = {
        "SOUL.md": "# Soul\n\n我是 Mini Agent，一个有帮助的 AI 助手。\n\n友善、简洁、准确。",
        "AGENTS.md": "# Agent Instructions\n\n- 先说意图，再调工具\n- 修改文件前先读取\n- 不确定时主动询问",
        "USER.md": "# User Profile\n\n（请编辑此文件来告诉 Bot 你的信息）",
    }
    for name, content in defaults.items():
        path = WORKSPACE / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")

# ── 工具系统（同第 2 章）────────────────────────────

class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]: ...
    @abstractmethod
    async def execute(self, **kwargs) -> str: ...
    def to_schema(self) -> dict:
        return {"type": "function", "function": {
            "name": self.name, "description": self.description,
            "parameters": self.parameters,
        }}

class ExecTool(Tool):
    @property
    def name(self): return "exec"
    @property
    def description(self): return "Execute a shell command."
    @property
    def parameters(self):
        return {"type": "object", "properties": {
            "command": {"type": "string", "description": "Shell command"},
        }, "required": ["command"]}
    async def execute(self, command: str, **kw) -> str:
        for bad in ["rm -rf", "mkfs", "dd if=", "shutdown"]:
            if bad in command.lower():
                return f"Error: Blocked ({bad})"
        try:
            proc = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
            r = out.decode(errors="replace")
            if err: r += f"\nSTDERR:\n{err.decode(errors='replace')}"
            return (r or "(no output)")[:10000]
        except Exception as e:
            return f"Error: {e}"

class ReadFileTool(Tool):
    @property
    def name(self): return "read_file"
    @property
    def description(self): return "Read file contents."
    @property
    def parameters(self):
        return {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path"},
        }, "required": ["path"]}
    async def execute(self, path: str, **kw) -> str:
        p = Path(path).expanduser()
        if not p.exists(): return f"Error: Not found: {path}"
        try: return p.read_text(encoding="utf-8")[:50000]
        except Exception as e: return f"Error: {e}"

class WriteFileTool(Tool):
    @property
    def name(self): return "write_file"
    @property
    def description(self): return "Write content to a file."
    @property
    def parameters(self):
        return {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "Content"},
        }, "required": ["path", "content"]}
    async def execute(self, path: str, content: str, **kw) -> str:
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} bytes to {p}"
        except Exception as e:
            return f"Error: {e}"

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    def register(self, tool: Tool):
        self._tools[tool.name] = tool
    def get_definitions(self) -> list[dict]:
        return [t.to_schema() for t in self._tools.values()]
    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if not tool: return f"Error: Unknown tool '{name}'"
        try: return await tool.execute(**params)
        except Exception as e: return f"Error: {e}"

# ── Session ──────────────────────────────────────────

@dataclass
class Session:
    key: str
    messages: list[dict] = field(default_factory=list)

    def get_history(self, max_messages: int = 50) -> list[dict]:
        recent = self.messages[-max_messages:]
        for i, m in enumerate(recent):
            if m.get("role") == "user":
                return recent[i:]
        return recent

class SessionManager:
    def __init__(self, workspace: Path):
        self.dir = workspace / "sessions"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        if key in self._cache: return self._cache[key]
        session = self._load(key) or Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session):
        path = self.dir / f"{session.key.replace(':', '_')}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for msg in session.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")

    def _load(self, key: str) -> Session | None:
        path = self.dir / f"{key.replace(':', '_')}.jsonl"
        if not path.exists(): return None
        msgs = [json.loads(l) for l in path.read_text("utf-8").splitlines() if l.strip()]
        return Session(key=key, messages=msgs)

# ── Context Builder ──────────────────────────────────

class ContextBuilder:
    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def build_system_prompt(self) -> str:
        parts = [f"# Mini Agent\n\n你是一个有帮助的 AI 助手。\n\n"
                 f"工作区: {self.workspace}\n"
                 f"长期记忆: {self.workspace}/memory/MEMORY.md"]
        for fn in self.BOOTSTRAP_FILES:
            p = self.workspace / fn
            if p.exists():
                parts.append(f"## {fn}\n\n{p.read_text('utf-8')}")
        mem = self.workspace / "memory" / "MEMORY.md"
        if mem.exists() and (t := mem.read_text("utf-8").strip()):
            parts.append(f"# Memory\n\n{t}")
        return "\n\n---\n\n".join(parts)

    def build_messages(self, history: list[dict], user_msg: str) -> list[dict]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": f"[Time: {now}]\n\n{user_msg}"},
        ]

# ── ReAct 循环 ───────────────────────────────────────

async def agent_loop(messages: list[dict], tools: ToolRegistry) -> str:
    for _ in range(10):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages,
            tools=tools.get_definitions() or None, temperature=0.1,
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]})
            for tc in msg.tool_calls:
                print(f"  [Tool] {tc.function.name}({tc.function.arguments[:80]})")
                result = await tools.execute(tc.function.name, json.loads(tc.function.arguments))
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            return msg.content or ""
    return "Max iterations reached."

# ── 主程序 ───────────────────────────────────────────

async def main():
    init_workspace()
    print(f"Mini Agent (workspace: {WORKSPACE})\n输入 exit 退出 | 输入 /new 清空会话\n")

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    ctx = ContextBuilder(WORKSPACE)
    sessions = SessionManager(WORKSPACE)
    session = sessions.get_or_create("cli:direct")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input == "/new":
            session = Session(key="cli:direct")
            sessions.save(session)
            print("New session started.\n")
            continue

        history = session.get_history(max_messages=50)
        messages = ctx.build_messages(history, user_input)

        reply = await agent_loop(messages, tools)

        # 保存本轮对话到 session
        session.messages.append({"role": "user", "content": user_input,
                                  "timestamp": datetime.now().isoformat()})
        session.messages.append({"role": "assistant", "content": reply,
                                  "timestamp": datetime.now().isoformat()})
        sessions.save(session)

        print(f"\nBot: {reply}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## 试一试

```bash
python mini_agent.py

# 第一次运行
You: 记住我叫小明，我喜欢用 Python

# 退出后再运行（对话历史被保留了！）
You: 我叫什么名字？
Bot: 你叫小明，你喜欢用 Python。
```

编辑 `~/.mini-agent/workspace/SOUL.md` 改成任何你想要的风格，下次对话自动生效。

## 关键对比

| 概念 | 我们的代码 | nanobot 的代码 |
|------|-----------|---------------|
| Session 持久化 | JSONL 简单序列化 | JSONL + metadata 行 + 缓存 + legacy 迁移 |
| Context Builder | 拼接 Bootstrap 文件 + Memory | 同上 + Skills 摘要 + Runtime Context + 最近历史摘要 |
| 记忆整合 | 简化版 JSON 解析 | Consolidator 写入 `history.jsonl` + Dream 整理 `SOUL.md` / `USER.md` / `MEMORY.md` |
| Bootstrap 文件 | 4 个 Markdown | 同样 4 个，但有模板同步机制 |

## 还缺什么？

Agent 现在有记忆、有个性，但它只能在终端里用。如果想让它在 Telegram / Discord 上工作呢？

下一章：消息总线——解耦 Agent 和 I/O。

## 配套示例

- 对应代码快照：[examples/part2/ch03-mini-agent-with-memory.py](../examples/part2/ch03-mini-agent-with-memory.py)
- 配套目录说明：[examples/part2/README.md](../examples/part2/README.md)
