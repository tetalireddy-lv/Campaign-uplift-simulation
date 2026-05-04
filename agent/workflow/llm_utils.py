"""LLM integration utilities — Azure OpenAI with API key auth."""
from __future__ import annotations

import json
import os
from pathlib import Path

_env = Path(__file__).resolve().parent.parent / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env, override=False)

from langchain_openai import AzureChatOpenAI

_llm: AzureChatOpenAI | None = None


def get_llm() -> AzureChatOpenAI:
    """Return the shared Azure OpenAI client, creating it once on first call."""
    global _llm
    if _llm is None:
        _llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],  # type: ignore[arg-type]
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            temperature=0.2,
        )
    return _llm


def call_llm_json(prompt: str) -> dict:
    """Call the LLM and return a parsed JSON dict. Raises on failure."""
    response = get_llm().invoke(prompt)
    content = response.content

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    return json.loads(content.strip())
