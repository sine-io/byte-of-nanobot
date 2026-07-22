"""Teaching snapshot for hero/01-simplest-agent.md."""

import os

from openai import OpenAI

API_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENROUTER_MODEL", "your-provider-supported-model")

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Create the client lazily so importing the teaching file needs no key."""
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("请先设置环境变量 OPENROUTER_API_KEY。")
        _client = OpenAI(base_url=API_BASE, api_key=api_key)
    return _client


def print_safety_warning() -> None:
    print("[安全提示] 这是教学示例，不是生产沙箱；它会把你的输入发送给配置的模型服务。")


def chat(messages: list[dict]) -> str:
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


def main():
    print_safety_warning()
    get_client()  # 启动时尽早验证凭据，但绝不打印凭据内容。
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
