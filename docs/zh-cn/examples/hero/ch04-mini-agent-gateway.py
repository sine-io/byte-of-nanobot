"""Teaching snapshot for hero/04-message-bus.md.

This runnable snapshot keeps the CLI channel enabled by default so it can run
without extra platform dependencies. See the chapter text for the Telegram
adapter example.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

API_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENROUTER_MODEL", "your-provider-supported-model")

_temporary_workspace = None


def select_workspace() -> Path:
    """Use an explicit teaching directory or create a private temporary one."""
    global _temporary_workspace
    configured = os.environ.get("NANOBOT_HERO_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    _temporary_workspace = tempfile.TemporaryDirectory(prefix="nanobot-hero-")
    return Path(_temporary_workspace.name).resolve()


WORKSPACE = select_workspace()

_client: OpenAI | None = None

_SAFE_COMMAND_OPTIONS = {
    "pwd": set(),
    "ls": {"-a", "-l", "-la", "-al", "--"},
    "cat": {"--"},
    "head": {"-n", "-c", "--"},
    "tail": {"-n", "-c", "--"},
    "wc": {"-c", "-l", "-m", "-w", "--"},
}
_OPTIONS_WITH_NUMBER = {"head": {"-n", "-c"}, "tail": {"-n", "-c"}}


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("请先设置环境变量 OPENROUTER_API_KEY。")
        _client = OpenAI(base_url=API_BASE, api_key=api_key)
    return _client


def resolve_workspace_path(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = WORKSPACE / candidate
    resolved = candidate.resolve(strict=False)
    if resolved != WORKSPACE and WORKSPACE not in resolved.parents:
        raise ValueError("path escapes the teaching workspace")
    return resolved


def parse_safe_command(command: str) -> list[str]:
    if any(marker in command for marker in ("\n", "\r", ";", "&", "|", ">", "<", "`", "$")):
        raise ValueError("shell operators are not allowed")
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"invalid command syntax: {exc}") from exc
    if not argv or argv[0] not in _SAFE_COMMAND_OPTIONS:
        allowed = ", ".join(sorted(_SAFE_COMMAND_OPTIONS))
        raise ValueError(f"command is not allowed; choose one of: {allowed}")

    executable = argv[0]
    safe_argv = [executable]
    index = 1
    paths_only = False
    while index < len(argv):
        argument = argv[index]
        if not paths_only and argument == "--":
            safe_argv.append(argument)
            paths_only = True
        elif not paths_only and argument.startswith("-"):
            if argument not in _SAFE_COMMAND_OPTIONS[executable]:
                raise ValueError(f"option is not allowed: {argument}")
            safe_argv.append(argument)
            if argument in _OPTIONS_WITH_NUMBER.get(executable, set()):
                index += 1
                if index >= len(argv) or not argv[index].isdigit():
                    raise ValueError(f"{argument} requires a non-negative integer")
                safe_argv.append(argv[index])
        else:
            safe_argv.append(str(resolve_workspace_path(argument)))
        index += 1

    if executable == "pwd" and len(safe_argv) != 1:
        raise ValueError("pwd does not accept arguments in this teaching example")
    return safe_argv


def print_safety_warning() -> None:
    print(
        "[安全提示] 教学 Gateway 不是生产沙箱。默认仅允许临时教学工作区内的文件，"
        "exec 也只开放少量只读命令；CLI Channel 不包含真实平台的鉴权边界。"
    )


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
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ExecTool(Tool):
    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Run one allowed read-only command inside the teaching workspace."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "One of: pwd, ls, cat, head, tail, wc; workspace paths only",
                },
            },
            "required": ["command"],
        }

    async def execute(self, command: str, **kwargs) -> str:
        try:
            WORKSPACE.mkdir(parents=True, exist_ok=True)
            argv = parse_safe_command(command)
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=str(WORKSPACE),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
            )
            try:
                out, err = await asyncio.wait_for(proc.communicate(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return "Error: Timeout"
            result = out.decode(errors="replace")
            if err:
                result += f"\nSTDERR:\n{err.decode(errors='replace')}"
            return (result or "(no output)")[:10000]
        except (OSError, ValueError) as exc:
            return f"Error: {exc}"


class ReadFileTool(Tool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read file contents."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
            },
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs) -> str:
        try:
            target = resolve_workspace_path(path)
            if not target.is_file():
                return f"Error: Not found: {path}"
            return target.read_text(encoding="utf-8")[:50000]
        except (OSError, UnicodeError, ValueError) as exc:
            return f"Error: {exc}"


class WriteFileTool(Tool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content"},
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, **kwargs) -> str:
        try:
            target = resolve_workspace_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} bytes to {target}"
        except (OSError, UnicodeError, ValueError) as exc:
            return f"Error: {exc}"


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict]:
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Unknown tool '{name}'"
        try:
            return await tool.execute(**params)
        except Exception as exc:
            return f"Error: {exc}"


@dataclass
class Session:
    key: str
    messages: list[dict] = field(default_factory=list)

    def get_history(self, max_messages: int = 50) -> list[dict]:
        recent = self.messages[-max_messages:]
        for index, message in enumerate(recent):
            if message.get("role") == "user":
                return recent[index:]
        return recent


class SessionManager:
    def __init__(self, workspace: Path):
        self.dir = workspace / "sessions"
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
        with open(path, "w", encoding="utf-8") as handle:
            for message in session.messages:
                handle.write(json.dumps(message, ensure_ascii=False) + "\n")

    def _load(self, key: str) -> Session | None:
        path = self.dir / f"{key.replace(':', '_')}.jsonl"
        if not path.exists():
            return None
        messages = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return Session(key=key, messages=messages)


class ContextBuilder:
    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md"]

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def build_system_prompt(self) -> str:
        parts = [
            f"# Mini Agent\n\n你是一个有帮助的 AI 助手。\n\n"
            f"工作区: {self.workspace}\n"
            f"长期记忆: {self.workspace}/memory/MEMORY.md"
        ]
        for filename in self.BOOTSTRAP_FILES:
            path = self.workspace / filename
            if path.exists():
                parts.append(f"## {filename}\n\n{path.read_text(encoding='utf-8')}")
        memory_file = self.workspace / "memory" / "MEMORY.md"
        if memory_file.exists():
            memory = memory_file.read_text(encoding="utf-8").strip()
            if memory:
                parts.append(f"# Memory\n\n{memory}")
        return "\n\n---\n\n".join(parts)

    def build_messages(self, history: list[dict], user_message: str) -> list[dict]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": f"[Time: {now}]\n\n{user_message}"},
        ]


@dataclass
class InboundMessage:
    channel: str
    sender_id: str
    chat_id: str
    content: str

    @property
    def session_key(self) -> str:
        return f"{self.channel}:{self.chat_id}"


@dataclass
class OutboundMessage:
    channel: str
    chat_id: str
    content: str


class MessageBus:
    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, message: InboundMessage):
        await self.inbound.put(message)

    async def consume_inbound(self) -> InboundMessage:
        return await self.inbound.get()

    async def publish_outbound(self, message: OutboundMessage):
        await self.outbound.put(message)

    async def consume_outbound(self) -> OutboundMessage:
        return await self.outbound.get()


class BaseChannel(ABC):
    name: str = "base"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    async def stop(self):
        ...

    @abstractmethod
    async def send(self, message: OutboundMessage):
        ...

    async def handle_message(self, sender_id: str, chat_id: str, content: str):
        await self.bus.publish_inbound(
            InboundMessage(channel=self.name, sender_id=sender_id, chat_id=chat_id, content=content)
        )


class CLIChannel(BaseChannel):
    name = "cli"

    async def start(self):
        loop = asyncio.get_running_loop()
        while True:
            user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            await self.handle_message("user", "direct", user_input)

    async def stop(self):
        return None

    async def send(self, message: OutboundMessage):
        print(f"\nBot: {message.content}\n")


class AgentLoop:
    def __init__(self, bus: MessageBus, tools: ToolRegistry, context: ContextBuilder, sessions: SessionManager):
        self.bus = bus
        self.tools = tools
        self.context = context
        self.sessions = sessions

    async def run(self):
        while True:
            try:
                message = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            session = self.sessions.get_or_create(message.session_key)
            history = session.get_history(max_messages=50)
            messages = self.context.build_messages(history, message.content)
            reply = await self._react_loop(messages)

            session.messages.append(
                {"role": "user", "content": message.content, "timestamp": datetime.now().isoformat()}
            )
            session.messages.append(
                {"role": "assistant", "content": reply, "timestamp": datetime.now().isoformat()}
            )
            self.sessions.save(session)

            await self.bus.publish_outbound(
                OutboundMessage(channel=message.channel, chat_id=message.chat_id, content=reply)
            )

    async def _react_loop(self, messages: list[dict]) -> str:
        for _ in range(10):
            response = get_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=self.tools.get_definitions() or None,
                temperature=0.1,
            )
            message = response.choices[0].message
            if message.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                            for tool_call in message.tool_calls
                        ],
                    }
                )
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    result = await self.tools.execute(tool_call.function.name, args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
            else:
                return message.content or ""
        return "Max iterations reached."


async def route_outbound(bus: MessageBus, channels: dict[str, BaseChannel]):
    while True:
        try:
            message = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        channel = channels.get(message.channel)
        if channel:
            await channel.send(message)


async def run_gateway():
    print_safety_warning()
    get_client()
    init_workspace()
    bus = MessageBus()

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    context = ContextBuilder(WORKSPACE)
    sessions = SessionManager(WORKSPACE)
    agent = AgentLoop(bus, tools, context, sessions)

    channels: dict[str, BaseChannel] = {
        "cli": CLIChannel(bus),
    }

    print(f"Gateway started. Channels: {list(channels.keys())}\n")

    await asyncio.gather(
        agent.run(),
        route_outbound(bus, channels),
        *[channel.start() for channel in channels.values()],
    )


if __name__ == "__main__":
    asyncio.run(run_gateway())
