"""Brief-to-Plan QA Tool — Validates plan alignment with original brief."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def validate_brief_to_plan(
    structured_brief: dict,
    execution_plan: dict,
    approved_assumptions: list,
) -> dict:
    """Validate that execution plan aligns with the original brief.

    Args:
        structured_brief: Parsed campaign brief
        execution_plan: Generated execution plan
        approved_assumptions: Manager-approved assumptions

    Returns:
        QA report with alignment score and findings
    """
    prompt = render_prompt(
        "qa/brief_to_plan_qa.j2",
        structured_brief=structured_brief,
        execution_plan=execution_plan,
        approved_assumptions=approved_assumptions,
    )
    return call_llm_json(prompt)


def calculate_alignment_score(qa_report: dict) -> int:
    """Deterministic alignment score from QA checks.

    Each dimension starts at 100/n points. Misalignment deducts.
    """
    checks = qa_report.get("checks", [])
    if not checks:
        return 0

    total = 0
    max_per_check = 100 / len(checks)

    status_scores = {
        "aligned": 1.0,
        "partially_aligned": 0.5,
        "misaligned": 0.0,
        "not_checked": 0.5,
    }

    for check in checks:
        status = check.get("status", "not_checked")
        total += max_per_check * status_scores.get(status, 0.5)

    return round(total)
