"""Execution Plan Generator Tool — Creates detailed task-level execution plan."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_execution_plan(
    structured_brief: dict,
    channel_strategy: dict,
) -> dict:
    """Generate the detailed execution plan.

    Args:
        structured_brief: Parsed campaign brief
        channel_strategy: Channel-level strategy

    Returns:
        Execution plan with tasks, owners, dependencies, and QA checkpoints
    """
    prompt = render_prompt(
        "planning/execution_plan_generator.j2",
        structured_brief=structured_brief,
        channel_strategy=channel_strategy,
    )
    return call_llm_json(prompt)
