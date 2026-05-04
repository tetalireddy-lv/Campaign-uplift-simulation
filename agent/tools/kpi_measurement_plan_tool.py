"""KPI & Measurement Plan Tool — deterministic measurement plan generator."""
from __future__ import annotations

from typing import Any


def _stringify_mapping(value: dict[str, Any]) -> str:
    return ", ".join(f"{key}: {item}" for key, item in value.items() if item not in (None, ""))


def _normalize_channels(structured_brief: dict, channel_strategy: dict | None) -> list[str]:
    channels = structured_brief.get("channels")
    if isinstance(channels, list):
        return [str(item) for item in channels]
    if isinstance(channels, str) and channels:
        return [part.strip() for part in channels.split(",") if part.strip()]
    strategy_channels = channel_strategy.get("channels") if channel_strategy else None
    if isinstance(strategy_channels, list):
        names = [str(item["channel"]) for item in strategy_channels if isinstance(item, dict) and item.get("channel")]
        if names:
            return names
    return ["Email", "Web Analytics"]


def _extract_primary_kpi(structured_brief: dict) -> tuple[str, str | None, str | None]:
    success_metrics = structured_brief.get("success_metrics")
    if isinstance(success_metrics, dict):
        primary = success_metrics.get("primary")
        if isinstance(primary, dict):
            metric = primary.get("metric") or primary.get("name") or primary.get("kpi")
            baseline = primary.get("baseline") or success_metrics.get("baseline")
            target = primary.get("target") or success_metrics.get("target")
            if metric:
                return str(metric), str(baseline) if baseline else None, str(target) if target else None
        if isinstance(primary, str) and primary:
            return str(primary), str(success_metrics.get("baseline") or ""), str(success_metrics.get("target") or "") or None
    if isinstance(success_metrics, str) and success_metrics:
        return success_metrics, None, None
    return "Primary KPI", None, None


def _timeline_window(structured_brief: dict) -> str:
    timeline = structured_brief.get("timeline")
    if isinstance(timeline, dict):
        return _stringify_mapping(timeline)
    return str(timeline) if timeline else "Campaign flight window"


def _data_sources_for_channels(channels: list[str]) -> list[str]:
    lowered = [c.lower() for c in channels]
    sources = {"CRM / CDP", "Campaign reporting dashboard"}
    if any(t in c for c in lowered for t in ["email", "in-app"]):
        sources.add("Marketing automation platform")
    if any(t in c for c in lowered for t in ["search", "social", "linkedin", "display", "programmatic"]):
        sources.add("Ad platform analytics")
    if any(t in c for c in lowered for t in ["direct mail", "event", "webinar"]):
        sources.add("Offline response and registration files")
    if any(t in c for c in lowered for t in ["web", "search", "social", "display"]):
        sources.add("Web analytics")
    return sorted(sources)


def generate_measurement_plan(
    structured_brief: dict,
    execution_plan: dict,
    channel_strategy: dict | None = None,
) -> dict:
    """Build a deterministic measurement plan for the Plan + Simulate step."""
    channels = _normalize_channels(structured_brief, channel_strategy)
    primary_kpi, baseline, target = _extract_primary_kpi(structured_brief)
    timeline = _timeline_window(structured_brief)
    cadence = "Weekly with mid-flight checkpoint" if any(t in timeline.lower() for t in ["90 days", "quarter", "13"]) else "Weekly"
    control_strategy = (
        "Geo holdout or staggered launch"
        if any(t in ", ".join(channels).lower() for t in ["direct mail", "event", "webinar"])
        else "Matched audience holdout"
    )

    return {
        "primary_kpi": primary_kpi,
        "baseline": baseline,
        "target": target,
        "measurement_framework": "Track the primary KPI at channel and total-campaign level, then compare against a holdout or staggered control where possible.",
        "measurement_window": timeline,
        "reporting_cadence": cadence,
        "data_sources": _data_sources_for_channels(channels),
        "control_strategy": control_strategy,
        "success_thresholds": {
            "minimum_success": baseline or "Baseline to be confirmed",
            "target_success": target or "Target to be confirmed",
        },
        "notes": [
            "Use the same KPI definition across channel, QA, and handoff outputs.",
            "Validate that attribution and holdout logic are approved before launch.",
        ],
        "owner": execution_plan.get("owner") or "Campaign Manager + Analytics",
    }
