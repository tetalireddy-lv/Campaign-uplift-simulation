"""Clarification Question Tool — Generates targeted questions for gap resolution."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def generate_clarification_questions(
    structured_brief: dict,
    gap_report: dict,
    compliance_report: dict,
    kpi_report: dict,
) -> list[dict]:
    """Generate prioritized clarification questions.

    Args:
        structured_brief: Parsed campaign brief
        gap_report: Identified gaps and risks
        compliance_report: Compliance findings
        kpi_report: KPI review findings

    Returns:
        List of clarification question objects
    """
    prompt = render_prompt(
        "ambiguity/clarification_questions.j2",
        structured_brief=structured_brief,
        gap_report=gap_report,
        compliance_report=compliance_report,
        kpi_report=kpi_report,
    )
    result = call_llm_json(prompt)
    return result.get("questions", [])
