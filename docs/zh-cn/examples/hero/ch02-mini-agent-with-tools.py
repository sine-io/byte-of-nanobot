"""Teaching snapshot for build/02-tool-system.md."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from openai import OpenAI

API_BASE = "https://openrouter.ai/api/v1"
API_KEY = "sk-or-v1-你的密钥"
MODEL = "your-provider-supported-model"

client = OpenAI(base_url=API_BASE, api_key=API_KEY)


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
        return "Execute a shell command and return output."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command"},
            },
            "required": ["command"],
        }

    async def execute(self, command: str, **kwargs) -> str:
        for bad in ["rm -rf", "mkfs", "dd if=", "shutdown"]:
            if bad in command.lower():
                return f"Error: Blocked ({bad})"
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
            result = out.decode(errors="replace")
            if err:
                result += f"\nSTDERR:\n{err.decode(errors='replace')}"
            return (result or "(no output)")[:10000]
        except asyncio.TimeoutError:
            return "Error: Timeout"
        except Exception as exc:
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
        target = Path(path).expanduser()
        if not target.exists():
            return f"Error: Not found: {path}"
        try:
            return target.read_text(encoding="utf-8")[:50000]
        except Exception as exc:
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
            target = Path(path).expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} bytes to {target}"
        except Exception as exc:
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
        response = client.chat.completions.create(
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
    print("Mini Agent with Tools (输入 exit 退出)\n")

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
