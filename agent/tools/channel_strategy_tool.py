"""Channel Strategy Tool — Generates channel-level execution strategy."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_channel_strategy(
    structured_brief: dict,
    orchestration_plan: dict,
) -> dict:
    """Generate detailed channel strategy.

    Args:
        structured_brief: Parsed campaign brief
        orchestration_plan: High-level orchestration plan

    Returns:
        Channel strategy with per-channel details
    """
    prompt = render_prompt(
        "planning/channel_strategy.j2",
        structured_brief=structured_brief,
        orchestration_plan=orchestration_plan,
    )
    return call_llm_json(prompt)
