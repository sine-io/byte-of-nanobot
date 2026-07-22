"""Teaching snapshot for hero/02-tool-system.md."""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import tempfile
from abc import ABC, abstractmethod
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
    """Resolve a model-supplied path and reject escapes or symlink escapes."""
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = WORKSPACE / candidate
    resolved = candidate.resolve(strict=False)
    if resolved != WORKSPACE and WORKSPACE not in resolved.parents:
        raise ValueError("path escapes the teaching workspace")
    return resolved


def parse_safe_command(command: str) -> list[str]:
    """Parse a tiny read-only command subset without invoking a shell."""
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
        "[安全提示] 教学工具不是生产沙箱。默认仅允许临时教学工作区内的文件，"
        "exec 也只开放少量只读命令；不要用它处理敏感数据。"
    )


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


async def agent_loop(messages: list[dict], tools: ToolRegistry) -> str:
    tool_defs = tools.get_definitions()

    for _ in range(10):
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tool_defs or None,
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
                print(f"  [Tool] {tool_call.function.name}({tool_call.function.arguments[:80]})")
                args = json.loads(tool_call.function.arguments)
                result = await tools.execute(tool_call.function.name, args)
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


async def main():
    print_safety_warning()
    get_client()
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    print(f"Mini Agent with Tools (workspace: {WORKSPACE})\n输入 exit 退出\n")

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    messages = [
        {
            "role": "system",
            "content": "你是一个有帮助的AI助手。你可以使用工具来完成任务。",
        }
    ]

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        reply = await agent_loop(messages, tools)
        messages.append({"role": "assistant", "content": reply})
        print(f"\nBot: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
