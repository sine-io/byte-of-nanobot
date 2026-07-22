"""Deterministic, offline tests for the five Hero teaching snapshots."""

from __future__ import annotations

import asyncio
import copy
import importlib.util
import json
import os
import socket
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPOSITORY_ROOT / "docs" / "zh-cn" / "examples" / "hero"


class NetworkAccessError(AssertionError):
    """Raised if an offline test accidentally attempts a network connection."""


class NeverNetworkOpenAI:
    """Import-compatible SDK placeholder that must never be instantiated."""

    def __init__(self, *args, **kwargs):
        raise NetworkAccessError("tests must inject FakeProvider before calling an example")


def _load_example(module_name: str, filename: str):
    """Load a hyphenated teaching file while replacing the optional OpenAI SDK."""
    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = NeverNetworkOpenAI
    path = EXAMPLES_ROOT / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load example: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        with mock.patch.dict(sys.modules, {"openai": fake_openai}):
            spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


CH01 = _load_example("hero_ch01", "ch01-mini-agent.py")
CH02 = _load_example("hero_ch02", "ch02-mini-agent-with-tools.py")
CH03 = _load_example("hero_ch03", "ch03-mini-agent-with-memory.py")
CH04 = _load_example("hero_ch04", "ch04-mini-agent-gateway.py")
CH05 = _load_example("hero_ch05", "ch05-skills-loader.py")


def _as_namespace(value):
    if isinstance(value, dict):
        return types.SimpleNamespace(**{key: _as_namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_as_namespace(item) for item in value]
    return value


class FakeHTTPResponse:
    """Small JSON response double used by the fake Provider transport."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.json_calls = 0

    def json(self) -> dict:
        self.json_calls += 1
        return copy.deepcopy(self._payload)


class FakeCompletions:
    def __init__(self, responses: list[FakeHTTPResponse]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("fake Provider has no response left")
        return _as_namespace(self.responses.pop(0).json())


class FakeProvider:
    """OpenAI-compatible shape backed only by in-memory HTTP response doubles."""

    def __init__(self, *payloads: dict):
        responses = [FakeHTTPResponse(payload) for payload in payloads]
        self.http_responses = responses
        self.completions = FakeCompletions(responses)
        self.chat = types.SimpleNamespace(completions=self.completions)


def assistant_payload(content: str = "", tool_calls: list[dict] | None = None) -> dict:
    return {
        "choices": [
            {
                "message": {
                    "content": content,
                    "tool_calls": tool_calls or [],
                }
            }
        ]
    }


def tool_call_payload(name: str, arguments: dict, call_id: str = "call-1") -> dict:
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


class HeroExamplesOfflineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.network_guard = mock.patch.object(
            socket,
            "create_connection",
            side_effect=NetworkAccessError("network access is forbidden in Hero tests"),
        )
        self.network_guard.start()
        self.addCleanup(self.network_guard.stop)

    def test_plain_reply_uses_fake_provider_and_http_response(self):
        provider = FakeProvider(assistant_payload("离线普通回复"))
        CH01._client = provider

        reply = CH01.chat([{"role": "user", "content": "你好"}])

        self.assertEqual(reply, "离线普通回复")
        self.assertEqual(provider.completions.calls[0]["messages"][0]["content"], "你好")
        self.assertEqual(provider.http_responses[0].json_calls, 1)

    async def test_tool_call_round_trip_is_driven_by_mock_data(self):
        calls: list[str] = []

        class RecordingTool(CH02.Tool):
            @property
            def name(self) -> str:
                return "record"

            @property
            def description(self) -> str:
                return "Record one value without external effects."

            @property
            def parameters(self) -> dict:
                return {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                }

            async def execute(self, value: str, **kwargs) -> str:
                calls.append(value)
                return f"recorded:{value}"

        provider = FakeProvider(
            assistant_payload(tool_calls=[tool_call_payload("record", {"value": "alpha"})]),
            assistant_payload("工具调用完成"),
        )
        CH02._client = provider
        registry = CH02.ToolRegistry()
        registry.register(RecordingTool())
        messages = [{"role": "user", "content": "记录 alpha"}]

        reply = await CH02.agent_loop(messages, registry)

        self.assertEqual(reply, "工具调用完成")
        self.assertEqual(calls, ["alpha"])
        tool_messages = [message for message in messages if message["role"] == "tool"]
        self.assertEqual(tool_messages[0]["content"], "recorded:alpha")
        self.assertEqual(len(provider.completions.calls), 2)

    async def test_tool_failure_is_returned_to_the_model(self):
        class FailingTool(CH02.Tool):
            @property
            def name(self) -> str:
                return "fail"

            @property
            def description(self) -> str:
                return "Fail deterministically."

            @property
            def parameters(self) -> dict:
                return {"type": "object", "properties": {}}

            async def execute(self, **kwargs) -> str:
                raise RuntimeError("mock tool failure")

        provider = FakeProvider(
            assistant_payload(tool_calls=[tool_call_payload("fail", {})]),
            assistant_payload("已向用户说明失败"),
        )
        CH02._client = provider
        registry = CH02.ToolRegistry()
        registry.register(FailingTool())
        messages = [{"role": "user", "content": "触发失败"}]

        reply = await CH02.agent_loop(messages, registry)

        self.assertEqual(reply, "已向用户说明失败")
        tool_result = next(message["content"] for message in messages if message["role"] == "tool")
        self.assertEqual(tool_result, "Error: mock tool failure")

    async def test_exec_timeout_kills_the_mock_process(self):
        class FakeProcess:
            def __init__(self):
                self.killed = False
                self.communicate_calls = 0

            async def communicate(self):
                self.communicate_calls += 1
                return b"", b""

            def kill(self):
                self.killed = True

        process = FakeProcess()

        async def fake_create_subprocess_exec(*args, **kwargs):
            return process

        async def fake_wait_for(awaitable, timeout):
            awaitable.close()
            raise asyncio.TimeoutError

        with (
            mock.patch.object(CH02.asyncio, "create_subprocess_exec", fake_create_subprocess_exec),
            mock.patch.object(CH02.asyncio, "wait_for", fake_wait_for),
        ):
            result = await CH02.ExecTool().execute("pwd")

        self.assertEqual(result, "Error: Timeout")
        self.assertTrue(process.killed)
        self.assertEqual(process.communicate_calls, 1)

    async def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            with mock.patch.object(CH02, "WORKSPACE", workspace):
                read_result = await CH02.ReadFileTool().execute("../outside.txt")
                write_result = await CH02.WriteFileTool().execute("../outside.txt", "blocked")

        self.assertIn("path escapes the teaching workspace", read_result)
        self.assertIn("path escapes the teaching workspace", write_result)

    async def test_dangerous_command_is_rejected_before_subprocess_creation(self):
        create_process = mock.AsyncMock(side_effect=AssertionError("must not execute"))
        with mock.patch.object(CH02.asyncio, "create_subprocess_exec", create_process):
            result = await CH02.ExecTool().execute("cat notes.txt; rm -rf .")

        self.assertIn("shell operators are not allowed", result)
        create_process.assert_not_awaited()

    def test_memory_example_persists_a_session_in_a_temporary_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            manager = CH03.SessionManager(workspace)
            session = CH03.Session(
                key="cli:test",
                messages=[{"role": "user", "content": "只存在临时目录"}],
            )
            manager.save(session)

            reloaded = CH03.SessionManager(workspace).get_or_create("cli:test")

        self.assertEqual(reloaded.messages, session.messages)

    async def test_gateway_react_loop_uses_the_fake_provider(self):
        provider = FakeProvider(assistant_payload("离线 Gateway 回复"))
        CH04._client = provider
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            agent = CH04.AgentLoop(
                CH04.MessageBus(),
                CH04.ToolRegistry(),
                CH04.ContextBuilder(workspace),
                CH04.SessionManager(workspace),
            )
            reply = await agent._react_loop([{"role": "user", "content": "ping"}])

        self.assertEqual(reply, "离线 Gateway 回复")

    def test_skills_example_prefers_workspace_and_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            builtin = root / "builtin"
            outside = root / "outside"
            workspace_weather = workspace / "skills" / "weather"
            builtin_weather = builtin / "weather"
            workspace_weather.mkdir(parents=True)
            builtin_weather.mkdir(parents=True)
            outside.mkdir()
            (workspace_weather / "SKILL.md").write_text(
                "---\nname: weather\ndescription: workspace version\n---\n",
                encoding="utf-8",
            )
            (builtin_weather / "SKILL.md").write_text(
                "---\nname: weather\ndescription: builtin version\n---\n",
                encoding="utf-8",
            )
            (outside / "SKILL.md").write_text("# outside", encoding="utf-8")
            os.symlink(outside, workspace / "skills" / "escape", target_is_directory=True)

            skills = CH05.SkillsLoader(workspace, builtin).list_skills()

        self.assertEqual([skill["name"] for skill in skills], ["weather"])
        self.assertEqual(skills[0]["description"], "workspace version")


if __name__ == "__main__":
    unittest.main()
