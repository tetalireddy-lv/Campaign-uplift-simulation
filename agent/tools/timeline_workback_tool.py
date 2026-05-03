"""Timeline Workback Tool — Creates reverse-engineered timeline from launch date."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_timeline(
    structured_brief: dict,
    execution_plan: dict,
) -> dict:
    """Generate workback timeline from launch date.

    Args:
        structured_brief: Parsed campaign brief
        execution_plan: Execution plan with tasks

    Returns:
        Timeline with milestones, critical path, and buffer analysis
    """
    prompt = render_prompt(
        "planning/timeline_workback.j2",
        structured_brief=structured_brief,
        execution_plan=execution_plan,
    )
    return call_llm_json(prompt)
