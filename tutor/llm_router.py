from __future__ import annotations

from typing import Any

from anthropic import Anthropic
from openai import OpenAI

from damodaran_context import DAMODARAN_SYSTEM_PROMPT


def _with_system_prompt(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"role": "system", "content": DAMODARAN_SYSTEM_PROMPT}, *messages]


def get_llm_response(messages: list[dict[str, str]], provider: str, api_key: str) -> str:
    if provider == "mock":
        return (
            "I'm running in offline mode. Please connect an LLM provider "
            "in the sidebar to chat with Professor Damodaran."
        )

    payload = _with_system_prompt(messages)

    if provider == "openai":
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model="gpt-4o", messages=payload)
        return response.choices[0].message.content or ""

    if provider == "groq":
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=payload
        )
        return response.choices[0].message.content or ""

    if provider == "anthropic":
        client = Anthropic(api_key=api_key)
        anthropic_messages: list[dict[str, Any]] = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=DAMODARAN_SYSTEM_PROMPT,
            messages=anthropic_messages,
            max_tokens=1024,
        )
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )

    raise ValueError(f"Unsupported provider: {provider}")
