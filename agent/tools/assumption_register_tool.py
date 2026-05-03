"""Assumption Register Tool — Creates explicit assumptions for gaps."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_assumptions(
    structured_brief: dict,
    gap_report: dict,
    clarification_questions: list,
) -> list[dict]:
    """Generate explicit assumptions for gaps that can be reasonably inferred.

    Args:
        structured_brief: Parsed campaign brief
        gap_report: Identified gaps
        clarification_questions: Generated questions

    Returns:
        List of assumption objects with confidence and risk
    """
    prompt = render_prompt(
        "ambiguity/assumption_register.j2",
        structured_brief=structured_brief,
        gap_report=gap_report,
        clarification_questions=clarification_questions,
    )
    result = call_llm_json(prompt)
    return result.get("assumptions", [])
