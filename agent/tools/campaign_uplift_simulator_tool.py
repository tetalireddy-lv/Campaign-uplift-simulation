"""Campaign Uplift Simulator Tool — deterministic, CSV-backed scenario simulation."""
from __future__ import annotations

import csv
import json
import random
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from data.scripts.generate_simulation_data import (
    BRIEFS_PATH,
    HISTORICAL_RESULTS_PATH,
    SEGMENTS_PATH,
    SIM_INPUTS_PATH,
    allocate_counts,
    assign_mode_and_confidence,
    audience_specificity_score,
    build_input_row,
    build_segment_profile,
    channel_specificity_score,
    generate_simulation_data,
    normalize_text,
)


MANAGER_EDITABLE_FIELDS = [
    "audience_size",
    "budget_numeric",
    "baseline_kpi_value",
    "target_kpi_value",
    "persuadables_pct",
    "sure_things_pct",
    "lost_causes_pct",
    "do_not_disturb_pct",
    "unknown_pct",
]

SEGMENT_EXPLANATIONS = {
    "persuadables": "Likely to convert because of the campaign.",
    "sure_things": "Likely to convert even without the campaign.",
    "lost_causes": "Unlikely to convert even with the campaign.",
    "do_not_disturb": "May respond negatively or create fatigue or cannibalization risk.",
    "unknown": "Not enough data to classify confidently.",
}


def calculate_deterministic_uplift(
    readiness_score: int,
    gap_count: int,
    critical_gaps: int,
) -> dict:
    """Retained helper for simple score-based uplift estimation."""
    gap_closure_uplift = min(50, gap_count * 5)
    critical_penalty = critical_gaps * 10
    current_pct = readiness_score
    clarified_min = min(100, current_pct + gap_closure_uplift - critical_penalty)
    clarified_max = min(100, current_pct + gap_closure_uplift + 10)
    optimized_min = min(100, clarified_min + 5)
    optimized_max = min(100, clarified_max + 15)
    return {
        "current_score": current_pct,
        "clarified_range": {"min": clarified_min, "max": clarified_max},
        "optimized_range": {"min": optimized_min, "max": optimized_max},
        "total_potential_uplift_pct": {
            "min": max(0, clarified_min - current_pct),
            "max": max(0, optimized_max - current_pct),
        },
    }


def _as_path(value: str | Path | None) -> Path:
    if value is None:
        return BRIEFS_PATH.parent
    return Path(value)


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _ensure_supporting_data(data_directory: Path) -> dict[str, Path]:
    paths = {
        "simulation_inputs": data_directory / SIM_INPUTS_PATH.name,
        "historical_results": data_directory / HISTORICAL_RESULTS_PATH.name,
        "segments": data_directory / SEGMENTS_PATH.name,
    }
    if not all(path.exists() for path in paths.values()):
        generate_simulation_data(source_path=data_directory / BRIEFS_PATH.name, output_dir=data_directory)
    return paths


@lru_cache(maxsize=8)
def _load_datasets_cached(data_directory: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    data_dir = Path(data_directory)
    paths = _ensure_supporting_data(data_dir)
    return (
        _read_csv_rows(paths["simulation_inputs"]),
        _read_csv_rows(paths["segments"]),
        _read_csv_rows(paths["historical_results"]),
    )


def _load_datasets(data_directory: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    return _load_datasets_cached(str(data_directory.resolve()))


def _stringify_mapping(value: dict[str, Any]) -> str:
    return ", ".join(f"{key}: {item}" for key, item in value.items() if item not in (None, ""))


def _normalize_target_audience(value: Any) -> str:
    if isinstance(value, dict):
        return _stringify_mapping(value)
    return str(value or "")


def _normalize_channels(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(str(key) for key in value)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "")


def _normalize_budget(value: Any) -> str:
    if isinstance(value, dict):
        total = value.get("total") or value.get("amount") or value.get("budget")
        if total not in (None, ""):
            try:
                return f"${float(total):,.0f}"
            except (TypeError, ValueError):
                return str(total)
        return _stringify_mapping(value)
    return str(value or "")


def _normalize_timeline(value: Any) -> str:
    if isinstance(value, dict):
        return _stringify_mapping(value)
    return str(value or "")


def _normalize_success_metrics(value: Any) -> str:
    if isinstance(value, dict):
        pieces: list[str] = []
        primary = value.get("primary")
        if isinstance(primary, dict):
            metric = primary.get("metric") or primary.get("name") or primary.get("kpi")
            baseline = primary.get("baseline")
            target = primary.get("target")
            if metric:
                pieces.append(str(metric))
            if baseline:
                pieces.append(f"baseline {baseline}")
            if target:
                pieces.append(f"target {target}")
        else:
            if primary:
                pieces.append(str(primary))
            if value.get("baseline"):
                pieces.append(f"baseline {value['baseline']}")
            if value.get("target"):
                pieces.append(f"target {value['target']}")
        if value.get("secondary"):
            pieces.append(f"secondary {value['secondary']}")
        return "; ".join(pieces)
    return str(value or "")


def _normalize_constraints(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value or "")


def _build_raw_row(structured_brief: dict, execution_plan: dict) -> dict[str, str]:
    channels = _normalize_channels(structured_brief.get("channels"))
    if not channels and execution_plan.get("channel_mix"):
        channels = _normalize_channels(execution_plan.get("channel_mix"))

    return {
        "Campaign Name": str(
            structured_brief.get("campaign_name")
            or execution_plan.get("campaign_name")
            or structured_brief.get("name")
            or "Campaign"
        ),
        "Business Objective": str(
            structured_brief.get("business_objective")
            or execution_plan.get("strategy_summary")
            or execution_plan.get("campaign_overview")
            or ""
        ),
        "Target Audience": _normalize_target_audience(structured_brief.get("target_audience")),
        "Key Message": str(structured_brief.get("key_message") or execution_plan.get("core_message") or ""),
        "Channels": channels,
        "Budget": _normalize_budget(structured_brief.get("budget") or execution_plan.get("budget_allocation")),
        "Timeline": _normalize_timeline(structured_brief.get("timeline")),
        "Success Metrics": _normalize_success_metrics(structured_brief.get("success_metrics")),
        "Constraints / Brand Notes": _normalize_constraints(structured_brief.get("constraints")),
    }


def _parse_assumptions(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(str(value))
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        return []
    return []


def _find_row_by_campaign_id(rows: list[dict[str, Any]], campaign_id: str | None) -> dict[str, Any] | None:
    if not campaign_id:
        return None
    return next((row for row in rows if row.get("campaign_id") == campaign_id), None)


def _find_row_by_name(rows: list[dict[str, Any]], campaign_name: str) -> dict[str, Any] | None:
    normalized_name = normalize_text(campaign_name)
    if not normalized_name:
        return None
    exact = next((row for row in rows if normalize_text(row.get("campaign_name")) == normalized_name), None)
    if exact:
        return exact
    return next(
        (
            row
            for row in rows
            if normalized_name in normalize_text(row.get("campaign_name"))
            or normalize_text(row.get("campaign_name")) in normalized_name
        ),
        None,
    )


def _find_row_by_combo(rows: list[dict[str, Any]], industry: str, campaign_type: str) -> dict[str, Any] | None:
    return next(
        (
            row
            for row in rows
            if row.get("industry") == industry and row.get("campaign_type") == campaign_type
        ),
        None,
    )


def _build_derived_row(structured_brief: dict, execution_plan: dict) -> tuple[dict[str, Any], dict[str, Any]]:
    raw_row = _build_raw_row(structured_brief, execution_plan)
    stable_seed = 20260503 + sum(ord(char) for char in raw_row["Campaign Name"])
    derived_row, metadata = build_input_row(raw_row, 9999, random.Random(stable_seed))
    derived_row["campaign_id"] = structured_brief.get("campaign_id") or "CMP_FALLBACK"
    return derived_row, metadata


def _build_history_sets(historical_rows: list[dict[str, Any]]) -> tuple[set[str], set[tuple[str, str]]]:
    exact_names = {str(row.get("campaign_name") or "") for row in historical_rows}
    combos = {
        (str(row.get("industry") or ""), str(row.get("campaign_type") or ""))
        for row in historical_rows
    }
    return exact_names, combos


def _rank_confidence(confidence: str) -> int:
    return {
        "Low": 0,
        "Medium": 1,
        "Medium-High": 2,
        "High": 3,
    }.get(confidence, 1)


def _confidence_label(rank: int) -> str:
    return {
        0: "Low",
        1: "Medium",
        2: "Medium-High",
        3: "High",
    }.get(max(0, min(rank, 3)), "Medium")


def _measurement_ready(measurement_plan: dict | None) -> bool:
    if not measurement_plan:
        return False
    keys = [
        "primary_kpi",
        "measurement_framework",
        "data_sources",
        "reporting_cadence",
        "control_strategy",
    ]
    return any(measurement_plan.get(key) for key in keys)


def _build_assumptions_used(
    structured_brief: dict,
    approved_assumptions: list,
    selected_row: dict[str, Any],
) -> list[dict[str, Any]]:
    assumptions = _parse_assumptions(selected_row.get("assumptions_used"))

    success_metrics = structured_brief.get("success_metrics")
    if isinstance(success_metrics, dict):
        baseline = success_metrics.get("baseline")
        target = success_metrics.get("target")
        if baseline:
            assumptions.append(
                {
                    "field": "Baseline KPI",
                    "value": baseline,
                    "source": "Provided in brief",
                    "editable_by_manager": True,
                }
            )
        if target:
            assumptions.append(
                {
                    "field": "Target KPI",
                    "value": target,
                    "source": "Provided in brief",
                    "editable_by_manager": True,
                }
            )

    budget = structured_brief.get("budget")
    if budget:
        assumptions.append(
            {
                "field": "Budget",
                "value": _normalize_budget(budget),
                "source": "Provided in brief",
                "editable_by_manager": True,
            }
        )

    for assumption in approved_assumptions or []:
        text = assumption.get("assumption") if isinstance(assumption, dict) else str(assumption)
        if text:
            assumptions.append(
                {
                    "field": assumption.get("id", "Approved Assumption") if isinstance(assumption, dict) else "Approved Assumption",
                    "value": text,
                    "source": "Manager approved",
                    "editable_by_manager": True,
                }
            )

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for assumption in assumptions:
        key = (str(assumption.get("field")), str(assumption.get("value")), str(assumption.get("source")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(assumption)
    return deduped


def _build_drivers_and_blockers(
    structured_brief: dict,
    execution_plan: dict,
    measurement_plan: dict | None,
    selected_row: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[list[str], list[str]]:
    drivers: list[str] = []
    blockers: list[str] = []

    audience_text = str(metadata.get("target_audience") or "")
    channels = str(metadata.get("channels") or "")
    constraints = str(metadata.get("constraints") or "")
    audience_score = audience_specificity_score(audience_text)
    channel_score = channel_specificity_score(channels)

    if audience_score >= 0.55:
        drivers.append("Audience specificity")
    else:
        blockers.append("Audience needs tighter definition")

    if channel_score >= 0.7:
        drivers.append("Channel-objective fit")
    else:
        blockers.append("Generic channel mix")

    if execution_plan.get("strategy_summary") or execution_plan.get("campaign_overview"):
        drivers.append("CTA alignment")
    else:
        blockers.append("CTA or offer path is underspecified")

    if _measurement_ready(measurement_plan):
        drivers.append("Measurement plan clarity")
    else:
        blockers.append("Measurement framework is incomplete")

    assumptions = _parse_assumptions(selected_row.get("assumptions_used"))
    if any(item.get("field") == "Budget" for item in assumptions):
        blockers.append("Budget missing or assumed")
    if any(item.get("field") == "Estimated Reach" for item in assumptions):
        blockers.append("Reach is estimated from channel assumptions")

    if any(term in normalize_text(constraints) for term in ["gdpr", "consent", "approval", "medical", "apr", "apy"]):
        blockers.append("Compliance review may slow activation")

    return drivers[:4], blockers[:4]


def _scenario_reason(blockers: list[str], drivers: list[str], mode: str, measurement_plan: dict | None, scenario: str) -> str:
    if scenario == "Current Brief As-Is":
        if blockers:
            return ", ".join(blockers[:3]) + "."
        return "The current brief is already specific enough to support a baseline estimate."
    if scenario == "Clarified Plan":
        clauses = []
        if blockers:
            clauses.append("Key blockers are reduced once missing details are clarified")
        if drivers:
            clauses.append("the existing strengths become easier to activate")
        if _measurement_ready(measurement_plan):
            clauses.append("measurement checkpoints are clearer")
        return ", and ".join(clauses) + "."
    if drivers:
        return ", ".join(drivers[:3]) + f" are fully aligned in {mode.lower()} mode."
    return "The optimized plan closes the most important execution and measurement gaps."


def _uplift_percent(expected_kpi_value: float, baseline_kpi_value: float) -> float:
    if baseline_kpi_value <= 0:
        return 0.0
    return round(((expected_kpi_value - baseline_kpi_value) / baseline_kpi_value) * 100, 1)


def _scenario_results(
    baseline: float,
    target: float,
    expected: float,
    confidence_level: str,
    blockers: list[str],
    drivers: list[str],
    mode: str,
    measurement_plan: dict | None,
) -> list[dict[str, Any]]:
    total_gap = max(target - baseline, 0.1)
    blocker_penalty = min(len(blockers) * 0.05, 0.2)
    driver_bonus = min(len(drivers) * 0.03, 0.12)

    current_factor = max(0.32, min(0.7, ((expected - baseline) / total_gap) - 0.16 - blocker_penalty))
    optimized_factor = min(0.94, max((expected - baseline) / total_gap + 0.14 + driver_bonus, 0.62))

    current_value = round(baseline + (total_gap * current_factor), 1)
    clarified_value = round(expected, 1)
    optimized_value = round(min(target, baseline + (total_gap * optimized_factor)), 1)

    base_rank = _rank_confidence(confidence_level)

    return [
        {
            "scenario": "Current Brief As-Is",
            "expected_kpi_value": current_value,
            "market_uplift_percent": _uplift_percent(current_value, baseline),
            "confidence": _confidence_label(max(0, base_rank - 1)),
            "reason": _scenario_reason(blockers, drivers, mode, measurement_plan, "Current Brief As-Is"),
        },
        {
            "scenario": "Clarified Plan",
            "expected_kpi_value": clarified_value,
            "market_uplift_percent": _uplift_percent(clarified_value, baseline),
            "confidence": _confidence_label(base_rank),
            "reason": _scenario_reason(blockers, drivers, mode, measurement_plan, "Clarified Plan"),
        },
        {
            "scenario": "Optimized Plan",
            "expected_kpi_value": optimized_value,
            "market_uplift_percent": _uplift_percent(optimized_value, baseline),
            "confidence": _confidence_label(min(3, base_rank + 1)),
            "reason": _scenario_reason(blockers, drivers, mode, measurement_plan, "Optimized Plan"),
        },
    ]


def _build_audience_mix(selected_row: dict[str, Any], segment_row: dict[str, Any] | None, metadata: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if segment_row is None:
        percentages, _, _ = build_segment_profile(
            str(selected_row["campaign_type"]),
            str(selected_row["industry"]),
            str(metadata.get("target_audience") or ""),
            str(metadata.get("channels") or ""),
            bool(metadata.get("budget_missing")),
            str(metadata.get("constraints") or ""),
        )
        counts = allocate_counts(int(selected_row["audience_size"]), percentages)
    else:
        percentages = {
            "persuadables": int(float(segment_row["persuadables_pct"])),
            "sure_things": int(float(segment_row["sure_things_pct"])),
            "lost_causes": int(float(segment_row["lost_causes_pct"])),
            "do_not_disturb": int(float(segment_row["do_not_disturb_pct"])),
            "unknown": int(float(segment_row["unknown_pct"])),
        }
        counts = {
            "persuadables": int(float(segment_row["persuadables_count"])),
            "sure_things": int(float(segment_row["sure_things_count"])),
            "lost_causes": int(float(segment_row["lost_causes_count"])),
            "do_not_disturb": int(float(segment_row["do_not_disturb_count"])),
            "unknown": int(float(segment_row["unknown_count"])),
        }

    return {
        segment: {
            "pct": percentages[segment],
            "count": counts[segment],
            "explanation": SEGMENT_EXPLANATIONS[segment],
        }
        for segment in ["persuadables", "sure_things", "lost_causes", "do_not_disturb", "unknown"]
    }


def _simulation_recommendation(mode: str, blockers: list[str]) -> str:
    if mode == "Historical-data":
        return "Proceed with benchmark-informed execution and monitor the first reporting checkpoint."
    if blockers:
        return "Clarify the current blockers before treating the uplift estimate as planning guidance."
    return "Proceed with the clarified plan and validate assumptions during the first measurement checkpoint."


def simulate_uplift(
    structured_brief: dict,
    execution_plan: dict,
    gap_report: dict | None = None,
    approved_assumptions: list | None = None,
    measurement_plan: dict | None = None,
    campaign_id: str | None = None,
    data_directory: str | Path | None = None,
) -> dict:
    """Run deterministic market uplift simulation backed by supporting CSVs.

    The simulator preserves backward compatibility with the existing signature by
    keeping `gap_report` as an optional positional argument while adding
    `measurement_plan`, `campaign_id`, and `data_directory` as optional inputs.
    """
    approved_assumptions = approved_assumptions or []
    data_dir = _as_path(data_directory)
    simulation_rows, segment_rows, historical_rows = _load_datasets(data_dir)

    derived_row, metadata = _build_derived_row(structured_brief, execution_plan)
    selected_row = (
        _find_row_by_campaign_id(simulation_rows, campaign_id or structured_brief.get("campaign_id"))
        or _find_row_by_name(simulation_rows, str(derived_row["campaign_name"]))
        or _find_row_by_combo(simulation_rows, str(derived_row["industry"]), str(derived_row["campaign_type"]))
        or derived_row
    )

    exact_history_names, history_combos = _build_history_sets(historical_rows)
    mode, confidence_level = assign_mode_and_confidence(
        selected_row,
        metadata,
        exact_history_names,
        history_combos,
    )
    if not _measurement_ready(measurement_plan):
        confidence_level = _confidence_label(max(0, _rank_confidence(confidence_level) - 1))

    segment_row = next(
        (
            row
            for row in segment_rows
            if row.get("campaign_id") == selected_row.get("campaign_id")
            or normalize_text(row.get("campaign_name")) == normalize_text(selected_row.get("campaign_name"))
        ),
        None,
    )

    baseline_kpi_value = round(float(selected_row["baseline_kpi_value"]), 1)
    target_kpi_value = round(float(selected_row["target_kpi_value"]), 1)
    expected_kpi_value = round(float(selected_row["expected_kpi_value"]), 1)
    market_uplift_percent = _uplift_percent(expected_kpi_value, baseline_kpi_value)

    drivers, blockers = _build_drivers_and_blockers(
        structured_brief,
        execution_plan,
        measurement_plan,
        selected_row,
        metadata,
    )
    scenario_results = _scenario_results(
        baseline=baseline_kpi_value,
        target=target_kpi_value,
        expected=expected_kpi_value,
        confidence_level=confidence_level,
        blockers=blockers,
        drivers=drivers,
        mode=mode,
        measurement_plan=measurement_plan,
    )
    audience_uplift_mix = _build_audience_mix(selected_row, segment_row, metadata)

    budget_numeric = float(selected_row["budget_numeric"])
    expected_revenue = float(selected_row["expected_campaign_revenue"])
    roi = round(((expected_revenue - budget_numeric) / budget_numeric) * 100, 1) if budget_numeric else 0.0

    result = {
        "campaign_id": selected_row.get("campaign_id", derived_row.get("campaign_id")),
        "simulation_mode": mode,
        "confidence_level": confidence_level,
        "primary_kpi": selected_row["baseline_kpi_name"],
        "baseline_kpi_value": baseline_kpi_value,
        "target_kpi_value": target_kpi_value,
        "expected_kpi_value": expected_kpi_value,
        "market_uplift_percent": market_uplift_percent,
        "scenario_results": scenario_results,
        "scenarios": scenario_results,
        "audience_uplift_mix": audience_uplift_mix,
        "assumptions_used": _build_assumptions_used(structured_brief, approved_assumptions, selected_row),
        "uplift_drivers": drivers,
        "uplift_blockers": blockers,
        "manager_editable_fields": MANAGER_EDITABLE_FIELDS,
        "warning": "This is a scenario estimate, not a guaranteed forecast. Assumed values should be reviewed by the campaign manager.",
        "expected_value": expected_kpi_value,
        "expected_campaign_revenue": expected_revenue,
        "roi": roi,
        "risk_factors": blockers,
        "recommendation": _simulation_recommendation(mode, blockers),
        "measurement_plan_used": bool(_measurement_ready(measurement_plan)),
        "_source": "deterministic",
    }

    result["uplift_summary"] = {
        "current_to_clarified": {
            "min_pct": scenario_results[1]["market_uplift_percent"] - scenario_results[0]["market_uplift_percent"],
            "max_pct": scenario_results[1]["market_uplift_percent"] - scenario_results[0]["market_uplift_percent"],
        },
        "clarified_to_optimized": {
            "min_pct": scenario_results[2]["market_uplift_percent"] - scenario_results[1]["market_uplift_percent"],
            "max_pct": scenario_results[2]["market_uplift_percent"] - scenario_results[1]["market_uplift_percent"],
        },
        "total_potential_uplift": {
            "min_pct": scenario_results[2]["market_uplift_percent"] - scenario_results[0]["market_uplift_percent"],
            "max_pct": scenario_results[2]["market_uplift_percent"] - scenario_results[0]["market_uplift_percent"],
        },
    }

    if gap_report:
        critical_gaps = [
            gap for gap in gap_report.get("gaps", [])
            if isinstance(gap, dict) and gap.get("severity") == "critical"
        ]
        if critical_gaps:
            result["uplift_blockers"] = result["uplift_blockers"] + [
                f"{len(critical_gaps)} critical readiness gap(s) still open"
            ]

    return result
