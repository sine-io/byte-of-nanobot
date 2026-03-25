"""Teaching snapshot for build/01-simplest-agent.md."""

from openai import OpenAI

API_BASE = "https://openrouter.ai/api/v1"
API_KEY = "sk-or-v1-你的密钥"
MODEL = "your-provider-supported-model"

client = OpenAI(base_url=API_BASE, api_key=API_KEY)


def chat(messages: list[dict]) -> str:
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
