"""Asset Checklist Tool — Generates complete asset requirements."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_asset_checklist(
    channel_strategy: dict,
    execution_plan: dict,
) -> dict:
    """Generate the complete asset checklist for the campaign.

    Args:
        channel_strategy: Channel-level strategy
        execution_plan: Execution plan

    Returns:
        Asset checklist with specs, owners, and deadlines
    """
    prompt = render_prompt(
        "planning/asset_checklist.j2",
        channel_strategy=channel_strategy,
        execution_plan=execution_plan,
    )
    return call_llm_json(prompt)
