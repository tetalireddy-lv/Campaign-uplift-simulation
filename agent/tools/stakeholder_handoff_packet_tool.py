"""Stakeholder Handoff Packet Tool — generates the final approval document."""
from __future__ import annotations

import sys
from typing import Any

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))


def _timeline_start(structured_brief: dict) -> str | None:
    timeline = structured_brief.get("timeline")
    if isinstance(timeline, dict):
        return timeline.get("start") or timeline.get("launch_date")
    return None


def _campaign_name(structured_brief: dict, execution_plan: dict) -> str:
    return str(
        structured_brief.get("campaign_name")
        or execution_plan.get("campaign_name")
        or execution_plan.get("campaign_overview")
        or "Campaign"
    )


def _format_mix(summary: dict[str, Any]) -> list[str]:
    lines = []
    for segment in ["persuadables", "sure_things", "lost_causes", "do_not_disturb", "unknown"]:
        details = summary.get(segment, {}) if isinstance(summary, dict) else {}
        if details:
            lines.append(f"{segment.replace('_', ' ').title()}: {details.get('pct')}% ({details.get('count')})")
    return lines


def generate_handoff_packet(
    structured_brief: dict,
    execution_plan: dict,
    channel_strategy: dict,
    simulation_report: dict,
    qa_report: dict,
    final_compliance_report: dict,
    approved_assumptions: list,
) -> dict:
    """Generate a deterministic stakeholder-ready handoff packet."""
    campaign_name = _campaign_name(structured_brief, execution_plan)
    primary_kpi = simulation_report.get("primary_kpi") or "Primary KPI"
    simulation_mode = simulation_report.get("simulation_mode") or "Assumption-based"
    warning = simulation_report.get("warning") or "This is a scenario estimate, not a guaranteed forecast."
    audience_mix = simulation_report.get("audience_uplift_mix") or {}

    stakeholder_sections = {
        "for_marketing_ops": [
            "Lock the execution plan, asset checklist, and launch timing before production begins.",
            f"Use the {simulation_mode.lower()} forecast as planning guidance, not as a promise.",
        ],
        "for_analytics": [
            f"Primary KPI: {primary_kpi}",
            f"Expected KPI value: {simulation_report.get('expected_kpi_value')}",
            "Validate measurement plan, reporting cadence, and holdout strategy before launch.",
        ],
        "for_legal": [
            str(note)
            for note in (final_compliance_report.get("notes") or final_compliance_report.get("compliance_checklist") or [])[:3]
        ] or ["Review channel targeting, claims, and consent handling before launch."],
        "for_stakeholders": [
            f"Mode: {simulation_mode}",
            f"Confidence: {simulation_report.get('confidence_level')}",
            *(_format_mix(audience_mix)[:3]),
        ],
    }

    risk_register = []
    risk_register.extend(simulation_report.get("uplift_blockers") or [])
    risk_register.extend(qa_report.get("critical_misalignments") or [])
    if isinstance(final_compliance_report.get("status"), str):
        risk_register.append(f"Compliance status: {final_compliance_report['status']}")
    if not risk_register:
        risk_register.append("No critical blockers were flagged, but assumptions still require manager review.")

    return {
        "campaign_name": campaign_name,
        "launch_date": _timeline_start(structured_brief),
        "status": "READY FOR APPROVAL — NOT LAUNCHED",
        "executive_summary": (
            f"{campaign_name} is ready for manager review. The current {simulation_mode.lower()} estimate projects "
            f"{primary_kpi} moving from {simulation_report.get('baseline_kpi_value')} to {simulation_report.get('expected_kpi_value')} "
            f"with {simulation_report.get('market_uplift_percent')}% uplift under the clarified plan."
        ),
        "stakeholder_sections": stakeholder_sections,
        "approved_assumptions": approved_assumptions,
        "risk_register": risk_register,
        "next_steps": [
            "Manager reviews the uplift assumptions and editable fields.",
            "Analytics validates the measurement plan and holdout approach.",
            "Marketing Ops confirms the timeline, assets, and owner handoffs.",
            "Legal and compliance teams approve any regulated claims or targeting rules before launch.",
        ],
        "important_notice": warning,
        "market_uplift_summary": {
            "simulation_mode": simulation_mode,
            "confidence_level": simulation_report.get("confidence_level"),
            "baseline_kpi": {
                "name": primary_kpi,
                "value": simulation_report.get("baseline_kpi_value"),
            },
            "target_kpi": simulation_report.get("target_kpi_value"),
            "expected_kpi": simulation_report.get("expected_kpi_value"),
            "market_uplift_percent": simulation_report.get("market_uplift_percent"),
            "audience_uplift_mix": audience_mix,
            "top_uplift_drivers": simulation_report.get("uplift_drivers") or [],
            "top_uplift_blockers": simulation_report.get("uplift_blockers") or [],
            "warning": warning,
        },
    }
