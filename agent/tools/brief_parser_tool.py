"""Brief Parser Tool — Parses raw campaign brief into structured format."""
from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def parse_brief(raw_brief: str) -> dict:
    """Parse a raw campaign brief into structured fields.

    Args:
        raw_brief: Unstructured campaign brief text

    Returns:
        Structured brief dictionary following brief_schema
    """
    prompt = render_prompt("parse_brief/brief_parser.j2", raw_brief=raw_brief)
    return call_llm_json(prompt)


if __name__ == "__main__":
    import json

    sample = """
    Campaign Name: Q4 Holiday Push
    Objective: Drive holiday sales for premium product line
    Audience: Existing customers aged 25-45
    Channels: Email, Instagram, Google Ads
    Budget: $120,000
    Timeline: Nov 1 - Dec 31
    """
    result = parse_brief(sample)
    print(json.dumps(result, indent=2))
