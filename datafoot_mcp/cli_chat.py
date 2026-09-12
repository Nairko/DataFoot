"""Chat terminal pour tester OpenAI + MCP avant Streamlit."""

import asyncio

from .openai_client import ask_openai


async def main() -> None:
    print("DataFootLLM CLI - tape 'quit' pour sortir")
    while True:
        question = input("\nVous > ").strip()
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        try:
            print(f"\nOpenAI > {await ask_openai(question)}")
        except Exception as error:
            print(f"\nErreur > {error}")


if __name__ == "__main__":
    asyncio.run(main())
