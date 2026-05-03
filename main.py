"""Main entry point — Run the Campaign Readiness Copilot workflow."""
from __future__ import annotations

import json
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.workflow import get_compiled_graph, CampaignReadinessState


def run_campaign_readiness(raw_brief: str, session_id: str | None = None) -> dict:
    """Run the full Campaign Readiness workflow on a raw brief.

    Args:
        raw_brief: Unstructured campaign brief text
        session_id: Optional session identifier

    Returns:
        Final workflow state with all artifacts
    """
    session_id = session_id or str(uuid.uuid4())

    initial_state: CampaignReadinessState = {
        "session_id": session_id,
        "raw_brief": raw_brief,
        "audit_trail": [],
        "current_step": "STARTED",
    }

    graph = get_compiled_graph()
    final_state = graph.invoke(initial_state)

    return final_state


def main():
    """CLI entry point."""
    if len(sys.argv) > 1:
        brief_path = Path(sys.argv[1])
        if brief_path.exists():
            raw_brief = brief_path.read_text(encoding="utf-8")
        else:
            raw_brief = " ".join(sys.argv[1:])
    else:
        # Sample brief for testing
        raw_brief = """
        Campaign Name: Q3 Enterprise Trial Conversion
        Business Objective: Convert 200 enterprise trial accounts to paid subscriptions by end of Q3 2026
        Target Audience: Enterprise IT decision-makers currently in 14-day trial, company size 500+
        Key Message: Your team is already seeing results — lock in your progress before trial ends
        Channels: Email, In-App, LinkedIn Ads
        Budget: $85,000 USD
        Timeline: June 1 - August 31, 2026
        Success Metrics: 40% trial-to-paid conversion rate (baseline: 22%)
        Constraints: No discount offers without VP approval. Must comply with enterprise data handling policy.
        """

    print(f"{'='*60}")
    print("Campaign Readiness Copilot")
    print(f"{'='*60}")
    print(f"\nProcessing brief ({len(raw_brief)} chars)...\n")

    result = run_campaign_readiness(raw_brief)

    print(f"\nWorkflow completed. Final step: {result.get('current_step')}")
    print(f"Readiness Score: {result.get('readiness_score', 'N/A')}")
    print(f"Audit Trail: {len(result.get('audit_trail', []))} entries")

    # Save output
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)
    output_file = output_path / f"result_{result['session_id'][:8]}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\nFull output saved to: {output_file}")


if __name__ == "__main__":
    main()
