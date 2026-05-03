"""Compliance & Brand Risk Tool — Reviews compliance and brand alignment."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def review_compliance(structured_brief: dict) -> dict:
    """Review campaign brief for compliance and brand risks.

    Args:
        structured_brief: Parsed campaign brief

    Returns:
        Compliance report with risk levels and findings
    """
    prompt = render_prompt(
        "readiness/compliance_risk_review.j2",
        structured_brief=structured_brief,
    )
    return call_llm_json(prompt)


def final_compliance_review(
    execution_plan: dict,
    channel_strategy: dict,
    compliance_report: dict,
) -> dict:
    """Final compliance check before handoff.

    Args:
        execution_plan: Generated execution plan
        channel_strategy: Channel strategy
        compliance_report: Previous compliance findings

    Returns:
        Final compliance status
    """
    prompt = render_prompt(
        "qa/final_compliance_review.j2",
        execution_plan=execution_plan,
        channel_strategy=channel_strategy,
        compliance_report=compliance_report,
    )
    return call_llm_json(prompt)
