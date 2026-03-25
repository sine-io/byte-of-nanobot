# 第 1 章：最简 Agent

> 用 40 行代码写一个能对话的 AI。

## 目标

写一个最小的程序：接收用户输入 → 发给 LLM → 打印回复 → 循环。

## 代码

```python
"""mini_agent.py — 最简 Agent，40 行"""

from openai import OpenAI

# 连接 LLM（OpenAI 兼容接口，支持 OpenRouter / DeepSeek / 本地模型等）
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # 换成你的 provider
    api_key="sk-or-v1-你的密钥",               # 换成你的 key
)
MODEL = "your-provider-supported-model"        # 换成你当前 provider 支持的模型

def chat(messages: list[dict]) -> str:
    """调用 LLM，返回回复文本。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
    )
    return response.choices[0].message.content or ""

def main():
    print("Mini Agent (输入 exit 退出)\n")

    messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
    ]

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"\nBot: {reply}\n")

if __name__ == "__main__":
    main()
```

运行：

```bash
python mini_agent.py
```

## 它做了什么？

```
用户输入 → 追加到 messages → 发给 LLM → 拿到回复 → 追加到 messages → 打印
                                                        ↑
                                            下一轮对话带上完整历史
```

关键设计：**messages 列表是有状态的**。每次对话都带上完整历史，LLM 才能理解上下文。这就是为什么它"记得"你之前说了什么。

## 对应 nanobot 的什么？

这 40 行代码对应 nanobot 中的两个模块：

### 1. Provider（`nanobot/providers/`）

我们的 `chat()` 函数就是一个最简的 Provider。nanobot 把它抽象成了类：

```python
# nanobot/providers/base.py（简化版）
class LLMProvider(ABC):
    async def chat(self, messages, tools=None, model=None, ...) -> LLMResponse:
        """调用 LLM 并返回结构化响应"""
        ...
```

nanobot 用 `LiteLLM` 库来统一多种 LLM 的 API 差异——不管你用 OpenAI、Anthropic 还是 DeepSeek，代码都一样。我们直接用 `openai` 库，因为它已经是事实上的通用接口标准。

### 2. 对话历史（`nanobot/session/manager.py`）

我们的 `messages` 列表就是一个最简的 Session。nanobot 把它持久化到磁盘：

```python
# nanobot/session/manager.py:17（简化版）
@dataclass
class Session:
    key: str                        # "telegram:123456"
    messages: list[dict] = field(default_factory=list)
    last_consolidated: int = 0      # 已整合的消息数
```

## 局限性

这个 40 行的 Agent 只能**聊天**。它不能：

- 执行命令、读写文件（没有工具）
- 记住跨会话的信息（重启就忘了）
- 连接 Telegram 等平台（只有终端）

## 本章你真正学到的抽象

这一章最重要的不是 40 行代码本身，而是两个基础抽象：

- `Provider`：负责把 `messages` 发给模型，再把回复取回来
- `Session` 的最小形态：一组按顺序累积的消息历史

后面所有复杂能力，几乎都建立在这两个前提之上。没有稳定的消息格式和对话状态，工具、记忆、多平台都无从谈起。

## 最小验证步骤

至少做下面 3 步验证：

1. 运行 `python mini_agent.py`，确认程序能进入交互循环
2. 连续问两句有关联的问题，确认第二句回答会利用第一句上下文
3. 输入 `exit` 或 `quit`，确认程序能正常退出

你应该观察到的现象：

- 第一轮有正常文本回复
- 第二轮不是“失忆式回答”
- 没有因为 API / model 配置错误而直接异常退出

## 常见失败点

- `401` / `Unauthorized`：API Key 无效，或 base URL / provider 不匹配
- 模型名报错：先确认该模型是否真的属于当前 provider
- 第二轮像没记忆：通常是 `messages.append(...)` 的顺序写错，或者没有把 assistant 回复也放回历史
- 返回结构不符合预期：不同 OpenAI 兼容接口在字段细节上可能略有差异，先打印 `response` 检查真实返回

下一章我们加上工具系统，让它从"聊天机器人"变成"AI Agent"。

---

[下一章：工具系统 →](02-tool-system.md)
