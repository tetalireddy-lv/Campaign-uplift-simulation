"""Brief Gap Detector Tool — Identifies missing, vague, and risky elements."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def detect_gaps(structured_brief: dict) -> dict:
    """Detect gaps, risks, and quality issues in a structured brief.

    Args:
        structured_brief: Parsed campaign brief dictionary

    Returns:
        Gap report with readiness score and identified issues
    """
    prompt = render_prompt("readiness/gap_detector.j2", structured_brief=structured_brief)
    return call_llm_json(prompt)


def calculate_readiness_score(gap_report: dict) -> int:
    """Deterministic readiness score calculation based on gap report.

    Scoring:
    - Start at 100
    - Critical gap: -20 each
    - High gap: -12 each
    - Medium gap: -6 each
    - Low gap: -3 each
    - Minimum score: 0
    """
    score = 100
    severity_penalties = {
        "critical": 20,
        "high": 12,
        "medium": 6,
        "low": 3,
    }

    for gap in gap_report.get("gaps", []):
        severity = gap.get("severity", "medium").lower()
        score -= severity_penalties.get(severity, 6)

    return max(0, score)
