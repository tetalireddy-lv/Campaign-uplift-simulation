"""Multi-Channel Consistency Tool — Checks cross-channel alignment."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def check_channel_consistency(
    channel_strategy: dict,
    execution_plan: dict,
) -> dict:
    """Check consistency across all campaign channels.

    Args:
        channel_strategy: Channel-level strategy
        execution_plan: Execution plan with tasks

    Returns:
        Consistency report with findings
    """
    prompt = render_prompt(
        "qa/multi_channel_consistency.j2",
        channel_strategy=channel_strategy,
        execution_plan=execution_plan,
    )
    return call_llm_json(prompt)
