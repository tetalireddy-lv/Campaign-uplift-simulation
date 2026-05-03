"""Generate deterministic market uplift support datasets from campaign briefs.

The raw `campaign_briefs.csv` remains untouched. This script derives three
supporting CSVs used by the market uplift simulator:

1. campaign_simulation_inputs.csv
2. historical_campaign_results.csv
3. campaign_uplift_segments.csv
"""
from __future__ import annotations

import csv
import json
import random
import re
from pathlib import Path
from typing import Any

from .generate_briefs import AUDIENCE_RANGES, BUDGET_RANGES, PRODUCT_NAMES


RANDOM_SEED = 20260503
DATA_DIR = Path(__file__).parent.parent / "raw"
BRIEFS_PATH = DATA_DIR / "campaign_briefs.csv"
SIM_INPUTS_PATH = DATA_DIR / "campaign_simulation_inputs.csv"
HISTORICAL_RESULTS_PATH = DATA_DIR / "historical_campaign_results.csv"
SEGMENTS_PATH = DATA_DIR / "campaign_uplift_segments.csv"

SIMULATION_INPUT_COLUMNS = [
    "campaign_id",
    "campaign_name",
    "industry",
    "campaign_type",
    "audience_size",
    "estimated_reach",
    "baseline_kpi_name",
    "baseline_kpi_value",
    "target_kpi_value",
    "expected_kpi_value",
    "market_uplift_percent",
    "average_order_value",
    "baseline_revenue",
    "expected_campaign_revenue",
    "budget_numeric",
    "simulation_mode",
    "confidence_level",
    "assumptions_used",
]

HISTORICAL_RESULTS_COLUMNS = [
    "historical_campaign_id",
    "campaign_name",
    "industry",
    "campaign_type",
    "audience_type",
    "channels",
    "budget",
    "audience_size",
    "treated_count",
    "control_count",
    "treated_conversion_rate",
    "control_conversion_rate",
    "incremental_lift_points",
    "relative_uplift_percent",
    "revenue_per_conversion",
    "campaign_revenue",
    "negative_response_rate",
    "unsubscribe_rate",
    "complaint_rate",
    "notes",
]

SEGMENT_COLUMNS = [
    "campaign_id",
    "campaign_name",
    "audience_size",
    "persuadables_pct",
    "sure_things_pct",
    "lost_causes_pct",
    "do_not_disturb_pct",
    "unknown_pct",
    "persuadables_count",
    "sure_things_count",
    "lost_causes_count",
    "do_not_disturb_count",
    "unknown_count",
    "segment_estimation_method",
    "segment_confidence",
    "segment_rationale",
]

BRAND_TO_INDUSTRY = {
    product.lower(): industry
    for industry, products in PRODUCT_NAMES.items()
    for product in products
}

TYPE_MARKERS = {
    "launch": "Product Launch",
    "trial conversion push": "Trial-to-Paid Conversion",
    "lead gen": "Lead Generation",
    "win-back": "Customer Reactivation",
    "upsell wave": "Upsell",
    "cross-sell drive": "Cross-sell",
    "loyalty boost": "Loyalty",
    "retention sprint": "Retention",
    "seasonal promo": "Seasonal Promotion",
    "event reg push": "Event Registration",
    "app adoption": "App Adoption",
    "renewal drive": "Renewal",
    "awareness": "Awareness",
}

INDUSTRY_KEYWORDS = {
    "Banking": ["bank", "fdic", "apr", "apy", "reg z", "deposit"],
    "Fintech": ["wallet", "fintech", "app users", "payment", "pay"],
    "Healthcare": ["medical", "patient", "clinic", "mlr", "health"],
    "Insurance": ["insurance", "policy", "claim", "underwriting"],
    "Education": ["student", "enrollment", "academy", "university", "scholar"],
    "Travel": ["travel", "hotel", "cruise", "flight", "voyage"],
    "Telecom": ["telecom", "fiber", "wireless", "mobile"],
    "E-commerce": ["e-commerce", "cart", "checkout", "shop", "order"],
    "B2C Retail": ["retail", "store", "sku", "merchandise"],
    "Consumer Subscription": ["subscription", "renewal", "monthly box", "crate"],
    "Events": ["conference", "summit", "expo", "event", "speaker", "sponsor"],
    "Professional Services": ["consulting", "advisory", "legal", "accounting"],
    "B2B SaaS": ["trial", "crm", "saas", "api", "enterprise", "workspace", "erp"],
}

CAMPAIGN_TYPE_KEYWORDS = {
    "Trial-to-Paid Conversion": ["trial", "trial-to-paid", "trial conversion"],
    "Lead Generation": ["lead", "mql", "sql"],
    "Customer Reactivation": ["reactivate", "win back", "lapsed", "inactive"],
    "Upsell": ["upsell", "higher tier", "premium"],
    "Cross-sell": ["cross-sell", "cross sell"],
    "Loyalty": ["loyalty", "repeat purchase", "member"],
    "Retention": ["retention", "retain", "keep customers"],
    "Seasonal Promotion": ["seasonal", "holiday", "fall", "summer", "spring", "winter", "promo"],
    "Event Registration": ["event registration", "register", "attendance", "summit", "conference"],
    "App Adoption": ["app adoption", "feature usage", "activate users"],
    "Renewal": ["renewal", "renew"],
    "Awareness": ["awareness", "reach", "impressions"],
    "Product Launch": ["launch", "new release", "introduce"],
}

KPI_DEFAULTS: dict[str, dict[str, Any]] = {
    "Trial-to-Paid Conversion": {"name": "Trial-to-paid conversion rate", "baseline": (11.0, 21.0), "lift": (4.0, 9.0)},
    "Lead Generation": {"name": "Lead conversion rate", "baseline": (4.0, 11.0), "lift": (2.0, 5.0)},
    "Customer Reactivation": {"name": "Reactivation rate", "baseline": (5.0, 16.0), "lift": (3.0, 7.0)},
    "Upsell": {"name": "Upsell conversion rate", "baseline": (3.0, 10.0), "lift": (1.5, 4.0)},
    "Cross-sell": {"name": "Cross-sell conversion rate", "baseline": (2.5, 9.0), "lift": (1.5, 4.5)},
    "Loyalty": {"name": "Repeat purchase rate", "baseline": (18.0, 42.0), "lift": (4.0, 9.0)},
    "Retention": {"name": "Retention rate", "baseline": (62.0, 82.0), "lift": (2.5, 6.0)},
    "Seasonal Promotion": {"name": "Conversion rate", "baseline": (1.1, 4.4), "lift": (0.8, 2.2)},
    "Event Registration": {"name": "Registration rate", "baseline": (7.0, 20.0), "lift": (2.0, 6.0)},
    "App Adoption": {"name": "Feature adoption rate", "baseline": (12.0, 36.0), "lift": (3.0, 8.0)},
    "Renewal": {"name": "Gross renewal rate", "baseline": (72.0, 89.0), "lift": (2.0, 5.5)},
    "Awareness": {"name": "Aided awareness lift", "baseline": (18.0, 45.0), "lift": (4.0, 11.0)},
    "Product Launch": {"name": "New sign-ups", "baseline": (1800.0, 7200.0), "lift_pct": (12.0, 32.0)},
}

AVERAGE_ORDER_VALUES = {
    "B2B SaaS": 1200,
    "B2C Retail": 110,
    "E-commerce": 95,
    "Banking": 650,
    "Fintech": 420,
    "Healthcare": 540,
    "Insurance": 780,
    "Education": 360,
    "Travel": 880,
    "Telecom": 470,
    "Consumer Subscription": 140,
    "Events": 520,
    "Professional Services": 1800,
}

SENSITIVE_INDUSTRIES = {"Healthcare", "Banking", "Fintech", "Insurance"}
DISCOUNT_HEAVY_INDUSTRIES = {"B2C Retail", "E-commerce", "Consumer Subscription", "Travel"}
HISTORY_EXCLUDED_COMBOS = {
    ("Healthcare", "Awareness"),
    ("Insurance", "Product Launch"),
    ("Fintech", "App Adoption"),
}
GENERIC_CHANNEL_TERMS = {"online", "digital", "social", "media", "paid media"}


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def read_briefs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def extract_currency_amount(text: str) -> float | None:
    match = re.search(r"\$\s*([\d,]+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def extract_percent(text: str, prefix: str) -> float | None:
    match = re.search(prefix + r"\s*([\d.]+)\s*%", text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def split_channels(channels: str) -> list[str]:
    raw = re.sub(r"\band\b", ",", channels or "", flags=re.IGNORECASE)
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    return parts or ["Unknown"]


def stable_roll(text: str) -> float:
    total = sum(ord(char) for char in text)
    return (total % 1000) / 1000


def infer_industry(row: dict[str, str]) -> str:
    campaign_name = normalize_text(row.get("Campaign Name"))
    context = " ".join(
        normalize_text(row.get(column))
        for column in [
            "Campaign Name",
            "Business Objective",
            "Target Audience",
            "Key Message",
            "Channels",
            "Constraints / Brand Notes",
        ]
    )

    for product_name, industry in BRAND_TO_INDUSTRY.items():
        if campaign_name.startswith(product_name):
            return industry

    scored: list[tuple[int, str]] = []
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in context)
        scored.append((score, industry))
    scored.sort(reverse=True)
    if scored and scored[0][0] > 0:
        return scored[0][1]

    industries = sorted(BUDGET_RANGES)
    return industries[int(stable_roll(campaign_name) * len(industries)) % len(industries)]


def infer_campaign_type(row: dict[str, str]) -> str:
    campaign_name = normalize_text(row.get("Campaign Name"))
    objective = normalize_text(row.get("Business Objective"))
    metrics = normalize_text(row.get("Success Metrics"))
    combined = f"{campaign_name} {objective} {metrics}"

    for marker, campaign_type in TYPE_MARKERS.items():
        if marker in campaign_name:
            return campaign_type

    scored: list[tuple[int, str]] = []
    for campaign_type, keywords in CAMPAIGN_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in combined)
        scored.append((score, campaign_type))
    scored.sort(reverse=True)
    if scored and scored[0][0] > 0:
        return scored[0][1]
    return "Lead Generation"


def detect_kpi_name(metric_text: str, campaign_type: str) -> str:
    metric_text = normalize_text(metric_text)
    if "trial" in metric_text:
        return "Trial-to-paid conversion rate"
    if "renewal" in metric_text:
        return "Gross renewal rate"
    if "reactivat" in metric_text or "win back" in metric_text:
        return "Reactivation rate"
    if "awareness" in metric_text:
        return "Aided awareness lift"
    if "ctr" in metric_text:
        return "CTR"
    if "roas" in metric_text:
        return "ROAS"
    if "revenue" in metric_text:
        return "Incremental revenue"
    if "sign-up" in metric_text or "signup" in metric_text:
        return "New sign-ups"
    if "registration" in metric_text:
        return "Registration rate"
    if "adoption" in metric_text:
        return "Feature adoption rate"
    return str(KPI_DEFAULTS[campaign_type]["name"])


def choose_default_kpi(campaign_type: str, rng: random.Random) -> tuple[str, float, float]:
    config = KPI_DEFAULTS[campaign_type]
    baseline_low, baseline_high = config["baseline"]
    baseline = round(rng.uniform(baseline_low, baseline_high), 1)

    if "lift" in config:
        lift_low, lift_high = config["lift"]
        target = round(baseline + rng.uniform(lift_low, lift_high), 1)
    else:
        pct_low, pct_high = config["lift_pct"]
        target = round(baseline * (1 + rng.uniform(pct_low, pct_high) / 100), 1)

    return str(config["name"]), baseline, target


def parse_success_metrics(metric_text: str, industry: str, campaign_type: str, rng: random.Random) -> tuple[str, float, float, list[dict[str, Any]], bool, bool]:
    metric_text = str(metric_text or "")
    metric_name = detect_kpi_name(metric_text, campaign_type)
    assumptions: list[dict[str, Any]] = []
    baseline_missing = False
    target_missing = False

    baseline_value = extract_percent(metric_text, r"baseline[:\s]+")
    target_value = extract_percent(metric_text, r"target[:\s]+")

    delta_match = re.search(r"target\s*\+\s*([\d.]+)\s*pt", metric_text, flags=re.IGNORECASE)
    if baseline_value is not None and delta_match:
        target_value = round(baseline_value + float(delta_match.group(1)), 1)

    improvement_match = re.search(r"lift .* by\s*([\d.]+)\s*%", metric_text, flags=re.IGNORECASE)
    if baseline_value is not None and improvement_match and target_value is None:
        target_value = round(baseline_value * (1 + float(improvement_match.group(1)) / 100), 1)

    roas_match = re.search(r"roas\s*(?:target|>=)?\s*([\d.]+)", metric_text, flags=re.IGNORECASE)
    if roas_match:
        metric_name = "ROAS"
        target_value = float(roas_match.group(1))

    count_target_match = re.search(r"target\s*\$?\s*([\d,]+(?:\.\d+)?)", metric_text, flags=re.IGNORECASE)
    if count_target_match and target_value is None and "%" not in count_target_match.group(0):
        numeric_target = float(count_target_match.group(1).replace(",", ""))
        if numeric_target > 100:
            target_value = numeric_target

    if metric_name == "Incremental revenue":
        target_value = target_value or extract_currency_amount(metric_text)

    if metric_name == "CTR" and baseline_value is None:
        baseline_value = None

    if baseline_value is None:
        default_name, default_baseline, default_target = choose_default_kpi(campaign_type, rng)
        baseline_value = default_baseline
        metric_name = metric_name or default_name
        baseline_missing = True
        assumptions.append(
            {
                "field": "Baseline KPI",
                "value": baseline_value,
                "source": f"Assumed from {industry} {campaign_type} benchmark",
                "editable_by_manager": True,
            }
        )
        if target_value is None:
            target_value = default_target

    if target_value is None:
        _, _, default_target = choose_default_kpi(campaign_type, rng)
        if default_target <= baseline_value:
            default_target = round(baseline_value * 1.18, 1)
        target_value = default_target
        target_missing = True
        assumptions.append(
            {
                "field": "Target KPI",
                "value": target_value,
                "source": f"Assumed from {industry} {campaign_type} benchmark",
                "editable_by_manager": True,
            }
        )

    if target_value <= baseline_value:
        target_value = round(baseline_value * 1.12, 1)
        target_missing = True
        assumptions.append(
            {
                "field": "Target KPI",
                "value": target_value,
                "source": "Adjusted to remain above baseline for deterministic uplift math",
                "editable_by_manager": True,
            }
        )

    return metric_name, round(baseline_value, 1), round(target_value, 1), assumptions, baseline_missing, target_missing


def parse_budget(budget_text: str, industry: str, rng: random.Random) -> tuple[int, list[dict[str, Any]], bool]:
    budget_text = str(budget_text or "")
    assumptions: list[dict[str, Any]] = []
    numeric_budget = extract_currency_amount(budget_text)
    budget_missing = numeric_budget is None
    if numeric_budget is None:
        low, high = BUDGET_RANGES[industry]
        numeric_budget = int(rng.randrange(low, high + 1, 500))
        assumptions.append(
            {
                "field": "Budget",
                "value": f"${numeric_budget:,.0f}",
                "source": f"Assumed from {industry} budget range",
                "editable_by_manager": True,
            }
        )
    return int(numeric_budget), assumptions, budget_missing


def audience_specificity_score(audience_text: str) -> float:
    audience_text = normalize_text(audience_text)
    if not audience_text:
        return 0.1

    score = 0.2
    specificity_markers = [
        r"\d",
        r"\b(age|aged|revenue|company size|annual|day|week|month|year|eu|apac|emea|mexico|germany|uk|us|dach|benelux|nordics)\b",
        r"\b(cfo|cto|vp|director|decision-makers|customers|subscribers|trial users|owners|patients)\b",
        r",",
    ]
    score += 0.15 * sum(1 for marker in specificity_markers if re.search(marker, audience_text))
    if any(term in audience_text for term in ["everyone", "all customers", "general audience", "consumers"]):
        score -= 0.15
    return max(0.05, min(score, 0.95))


def estimate_audience_size(industry: str, audience_text: str, rng: random.Random) -> int:
    low, high = AUDIENCE_RANGES[industry]
    specificity = audience_specificity_score(audience_text)
    # Specific audiences resolve toward the smaller end of the industry range.
    center = low + (high - low) * (1 - specificity)
    variance = (high - low) * 0.08
    estimate = int(center + rng.uniform(-variance, variance))
    return max(low, min(high, estimate))


def channel_specificity_score(channels: str) -> float:
    channel_list = [normalize_text(part) for part in split_channels(channels)]
    if not channel_list:
        return 0.1
    score = 0.0
    for channel in channel_list:
        if channel in GENERIC_CHANNEL_TERMS:
            score += 0.2
        elif any(term in channel for term in ["email", "direct mail", "paid search", "linkedin", "in-app", "webinar"]):
            score += 0.9
        elif any(term in channel for term in ["programmatic", "display", "paid social", "organic social", "pr"]):
            score += 0.65
        else:
            score += 0.45
    return max(0.1, min(score / len(channel_list), 0.95))


def estimate_reach(audience_size: int, channels: str) -> int:
    specificity = channel_specificity_score(channels)
    channel_count = len(split_channels(channels))
    reach_ratio = min(0.92, max(0.18, 0.24 + (specificity * 0.42) + (min(channel_count, 5) * 0.05)))
    return max(1, min(audience_size, int(audience_size * reach_ratio)))


def is_rate_metric(metric_name: str) -> bool:
    metric_name = normalize_text(metric_name)
    return any(term in metric_name for term in ["rate", "ctr", "roas", "awareness", "%"])


def estimate_achievement_factor(
    campaign_type: str,
    audience_text: str,
    channels: str,
    budget_missing: bool,
    baseline_missing: bool,
    target_missing: bool,
    constraints_text: str,
) -> float:
    factor = 0.56
    if campaign_type in {"Trial-to-Paid Conversion", "Customer Reactivation", "Retention", "Renewal"}:
        factor += 0.08
    if audience_specificity_score(audience_text) >= 0.55:
        factor += 0.07
    if channel_specificity_score(channels) >= 0.7:
        factor += 0.06
    if budget_missing:
        factor -= 0.06
    if baseline_missing:
        factor -= 0.03
    if target_missing:
        factor -= 0.02
    if any(term in normalize_text(constraints_text) for term in ["gdpr", "medical legal", "apr", "approval", "consent"]):
        factor -= 0.04
    return max(0.38, min(factor, 0.86))


def estimate_campaign_revenue(
    metric_name: str,
    metric_value: float,
    estimated_reach: int,
    budget_numeric: int,
    average_order_value: int,
) -> float:
    metric_name = normalize_text(metric_name)
    if "revenue" in metric_name:
        return round(metric_value, 2)
    if "roas" in metric_name:
        return round(metric_value * budget_numeric, 2)

    if "awareness" in metric_name:
        conversions = estimated_reach * (metric_value / 100) * 0.12
    elif "ctr" in metric_name:
        conversions = estimated_reach * (metric_value / 100) * 0.2
    elif is_rate_metric(metric_name):
        conversions = estimated_reach * (metric_value / 100)
    else:
        conversions = metric_value
    return round(conversions * average_order_value, 2)


def normalize_percentages(values: dict[str, float]) -> dict[str, int]:
    rounded = {key: max(0, int(value)) for key, value in values.items()}
    current = sum(rounded.values())
    if current == 100:
        return rounded

    # Sort keys: highest fractional remainder first (best candidates to round up).
    remainders = sorted(
        ((values[key] - rounded[key], key) for key in values),
        reverse=True,
    )
    keys_high_first = [key for _, key in remainders]
    keys_low_first = keys_high_first[::-1]

    if current < 100:
        # Distribute additions to keys with the largest fractional remainder first.
        needed = 100 - current
        i = 0
        while needed > 0:
            key = keys_high_first[i % len(keys_high_first)]
            rounded[key] += 1
            needed -= 1
            i += 1
    else:
        # Remove excess from keys with the smallest fractional remainder first.
        # Loop around as many times as needed — excess may exceed the key count.
        excess = current - 100
        i = 0
        while excess > 0:
            key = keys_low_first[i % len(keys_low_first)]
            if rounded[key] > 0:
                rounded[key] -= 1
                excess -= 1
            i += 1
    return rounded


def allocate_counts(total: int, percentages: dict[str, int]) -> dict[str, int]:
    counts = {key: int(total * pct / 100) for key, pct in percentages.items()}
    remainder = total - sum(counts.values())
    ordered_keys = sorted(percentages, key=lambda key: percentages[key], reverse=True)
    index = 0
    while remainder > 0:
        counts[ordered_keys[index % len(ordered_keys)]] += 1
        remainder -= 1
        index += 1
    return counts


def build_segment_profile(
    campaign_type: str,
    industry: str,
    audience_text: str,
    channels: str,
    budget_missing: bool,
    constraints_text: str,
) -> tuple[dict[str, int], str, str]:
    raw = {
        "persuadables": 30.0,
        "sure_things": 23.0,
        "lost_causes": 23.0,
        "do_not_disturb": 10.0,
        "unknown": 14.0,
    }
    rationales: list[str] = []

    if campaign_type in {"Trial-to-Paid Conversion", "Customer Reactivation", "Retention"}:
        raw["persuadables"] += 8
        raw["unknown"] -= 3
        raw["lost_causes"] -= 2
        rationales.append("Lifecycle conversion campaigns lift persuadables because message timing is closer to purchase intent.")

    if industry in DISCOUNT_HEAVY_INDUSTRIES and campaign_type in {"Seasonal Promotion", "Loyalty", "Customer Reactivation"}:
        raw["sure_things"] += 7
        raw["do_not_disturb"] += 4
        raw["persuadables"] -= 4
        rationales.append("Discount-heavy retail and subscription campaigns increase sure-things and cannibalization risk.")

    if industry in SENSITIVE_INDUSTRIES or any(term in normalize_text(constraints_text) for term in ["gdpr", "consent", "apr", "apy", "medical", "dsar"]):
        raw["do_not_disturb"] += 6
        raw["unknown"] += 4
        raw["persuadables"] -= 5
        rationales.append("Regulated or privacy-sensitive campaigns raise do-not-disturb and unknown shares.")

    if audience_specificity_score(audience_text) <= 0.35:
        raw["unknown"] += 8
        raw["persuadables"] -= 4
        rationales.append("Vague audiences expand the unknown segment.")
    else:
        raw["persuadables"] += 5
        raw["unknown"] -= 3
        rationales.append("Specific audience criteria increase persuadables because targeting is tighter.")

    if channel_specificity_score(channels) >= 0.7:
        raw["persuadables"] += 4
        raw["unknown"] -= 2
        rationales.append("Specific channels improve match quality and reduce unknown exposure.")
    else:
        raw["unknown"] += 5
        rationales.append("Generic channels reduce segmentation confidence.")

    if budget_missing:
        raw["unknown"] += 4
        raw["persuadables"] -= 2
        rationales.append("Missing or vague budget reduces confidence in reachable persuadables.")

    percentages = normalize_percentages(raw)

    confidence = "Medium"
    if industry in SENSITIVE_INDUSTRIES and audience_specificity_score(audience_text) <= 0.35:
        confidence = "Low"
    elif audience_specificity_score(audience_text) >= 0.6 and channel_specificity_score(channels) >= 0.7 and not budget_missing:
        confidence = "High"

    rationale = " ".join(rationales)
    return percentages, confidence, rationale


def build_input_row(row: dict[str, str], index: int, rng: random.Random) -> tuple[dict[str, Any], dict[str, Any]]:
    campaign_id = f"CMP_{index:04d}"
    campaign_name = row["Campaign Name"].strip()
    industry = infer_industry(row)
    campaign_type = infer_campaign_type(row)
    metric_name, baseline_value, target_value, metric_assumptions, baseline_missing, target_missing = parse_success_metrics(
        row.get("Success Metrics", ""),
        industry,
        campaign_type,
        rng,
    )
    budget_numeric, budget_assumptions, budget_missing = parse_budget(row.get("Budget", ""), industry, rng)
    audience_size = estimate_audience_size(industry, row.get("Target Audience", ""), rng)
    estimated_reach = estimate_reach(audience_size, row.get("Channels", ""))
    achievement_factor = estimate_achievement_factor(
        campaign_type,
        row.get("Target Audience", ""),
        row.get("Channels", ""),
        budget_missing,
        baseline_missing,
        target_missing,
        row.get("Constraints / Brand Notes", ""),
    )
    expected_kpi_value = round(baseline_value + ((target_value - baseline_value) * achievement_factor), 1)
    market_uplift_percent = round(((expected_kpi_value - baseline_value) / baseline_value) * 100, 1)

    average_order_value = AVERAGE_ORDER_VALUES[industry]
    baseline_revenue = estimate_campaign_revenue(metric_name, baseline_value, estimated_reach, budget_numeric, average_order_value)
    expected_campaign_revenue = estimate_campaign_revenue(metric_name, expected_kpi_value, estimated_reach, budget_numeric, average_order_value)

    assumptions: list[dict[str, Any]] = []
    assumptions.extend(metric_assumptions)
    assumptions.extend(budget_assumptions)
    assumptions.append(
        {
            "field": "Industry",
            "value": industry,
            "source": "Inferred from campaign naming and brief context",
            "editable_by_manager": True,
        }
    )
    assumptions.append(
        {
            "field": "Campaign Type",
            "value": campaign_type,
            "source": "Inferred from campaign name and business objective",
            "editable_by_manager": True,
        }
    )
    assumptions.append(
        {
            "field": "Audience Size",
            "value": audience_size,
            "source": "Estimated from industry range and audience specificity",
            "editable_by_manager": True,
        }
    )
    assumptions.append(
        {
            "field": "Estimated Reach",
            "value": estimated_reach,
            "source": "Estimated from channel specificity",
            "editable_by_manager": True,
        }
    )

    row_data = {
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "industry": industry,
        "campaign_type": campaign_type,
        "audience_size": audience_size,
        "estimated_reach": estimated_reach,
        "baseline_kpi_name": metric_name,
        "baseline_kpi_value": round(baseline_value, 1),
        "target_kpi_value": round(target_value, 1),
        "expected_kpi_value": round(expected_kpi_value, 1),
        "market_uplift_percent": round(market_uplift_percent, 1),
        "average_order_value": average_order_value,
        "baseline_revenue": round(baseline_revenue, 2),
        "expected_campaign_revenue": round(expected_campaign_revenue, 2),
        "budget_numeric": budget_numeric,
        "simulation_mode": "",
        "confidence_level": "",
        "assumptions_used": json.dumps(assumptions),
    }

    metadata = {
        "budget_missing": budget_missing,
        "baseline_missing": baseline_missing,
        "target_missing": target_missing,
        "channels": row.get("Channels", ""),
        "target_audience": row.get("Target Audience", ""),
        "constraints": row.get("Constraints / Brand Notes", ""),
        "metric_name": metric_name,
    }
    return row_data, metadata


def build_historical_row(
    historical_campaign_id: str,
    input_row: dict[str, Any],
    source_row: dict[str, str],
    metadata: dict[str, Any],
    rng: random.Random,
) -> dict[str, Any]:
    audience_size = int(input_row["audience_size"])
    control_count = max(100, int(audience_size * (0.16 + rng.uniform(0.02, 0.08))))
    treated_count = max(100, audience_size - control_count)

    baseline_kpi = float(input_row["baseline_kpi_value"])
    expected_kpi = float(input_row["expected_kpi_value"])
    control_rate = round(max(0.3, baseline_kpi * (0.92 + rng.uniform(-0.03, 0.03))), 2)
    treated_rate = round(max(control_rate + 0.1, expected_kpi * (0.94 + rng.uniform(-0.02, 0.03))), 2)
    incremental_lift_points = round(treated_rate - control_rate, 2)
    relative_uplift_percent = round((incremental_lift_points / control_rate) * 100, 1) if control_rate else 0.0

    negative_response_rate = 0.8
    unsubscribe_rate = 0.4
    complaint_rate = 0.1
    if input_row["industry"] in SENSITIVE_INDUSTRIES:
        negative_response_rate += 0.6
        unsubscribe_rate += 0.3
        complaint_rate += 0.12
    if channel_specificity_score(source_row.get("Channels", "")) < 0.5:
        unsubscribe_rate += 0.2
        complaint_rate += 0.05

    campaign_revenue = estimate_campaign_revenue(
        str(metadata["metric_name"]),
        treated_rate,
        int(input_row["estimated_reach"]),
        int(input_row["budget_numeric"]),
        int(input_row["average_order_value"]),
    )

    audience_type = "Specific" if audience_specificity_score(source_row.get("Target Audience", "")) >= 0.55 else "Broad"

    return {
        "historical_campaign_id": historical_campaign_id,
        "campaign_name": input_row["campaign_name"],
        "industry": input_row["industry"],
        "campaign_type": input_row["campaign_type"],
        "audience_type": audience_type,
        "channels": source_row.get("Channels", ""),
        "budget": int(input_row["budget_numeric"]),
        "audience_size": audience_size,
        "treated_count": treated_count,
        "control_count": control_count,
        "treated_conversion_rate": treated_rate,
        "control_conversion_rate": control_rate,
        "incremental_lift_points": incremental_lift_points,
        "relative_uplift_percent": relative_uplift_percent,
        "revenue_per_conversion": int(input_row["average_order_value"]),
        "campaign_revenue": round(campaign_revenue, 2),
        "negative_response_rate": round(negative_response_rate, 2),
        "unsubscribe_rate": round(unsubscribe_rate, 2),
        "complaint_rate": round(complaint_rate, 2),
        "notes": "Deterministic benchmark synthesized from the raw brief's industry, campaign type, and KPI structure.",
    }


def assign_mode_and_confidence(
    input_row: dict[str, Any],
    metadata: dict[str, Any],
    exact_history_names: set[str],
    history_combos: set[tuple[str, str]],
) -> tuple[str, str]:
    campaign_name = str(input_row["campaign_name"])
    combo = (str(input_row["industry"]), str(input_row["campaign_type"]))
    if campaign_name in exact_history_names:
        mode = "Historical-data"
        confidence = "High"
    elif combo in history_combos:
        mode = "Similar-campaign benchmark"
        confidence = "Medium"
    else:
        mode = "Assumption-based"
        confidence = "Medium"

    if metadata["budget_missing"] or channel_specificity_score(str(metadata["channels"])) < 0.5:
        confidence = "Low" if mode == "Assumption-based" else "Medium"
    elif audience_specificity_score(str(metadata["target_audience"])) >= 0.6 and not metadata["budget_missing"] and mode != "Assumption-based":
        confidence = "High" if mode == "Historical-data" else "Medium"
    return mode, confidence


def generate_simulation_data(
    source_path: Path = BRIEFS_PATH,
    output_dir: Path = DATA_DIR,
    seed: int = RANDOM_SEED,
) -> dict[str, Path]:
    rng = random.Random(seed)
    brief_rows = read_briefs(source_path)

    simulation_rows: list[dict[str, Any]] = []
    segment_rows: list[dict[str, Any]] = []
    historical_rows: list[dict[str, Any]] = []
    metadata_by_campaign: dict[str, dict[str, Any]] = {}

    historical_counter = 1
    for index, brief_row in enumerate(brief_rows, start=1):
        input_row, metadata = build_input_row(brief_row, index, rng)
        simulation_rows.append(input_row)
        metadata_by_campaign[str(input_row["campaign_id"])] = metadata

        percentages, segment_confidence, segment_rationale = build_segment_profile(
            str(input_row["campaign_type"]),
            str(input_row["industry"]),
            str(brief_row.get("Target Audience", "")),
            str(brief_row.get("Channels", "")),
            bool(metadata["budget_missing"]),
            str(brief_row.get("Constraints / Brand Notes", "")),
        )
        counts = allocate_counts(int(input_row["audience_size"]), percentages)
        segment_rows.append(
            {
                "campaign_id": input_row["campaign_id"],
                "campaign_name": input_row["campaign_name"],
                "audience_size": input_row["audience_size"],
                "persuadables_pct": percentages["persuadables"],
                "sure_things_pct": percentages["sure_things"],
                "lost_causes_pct": percentages["lost_causes"],
                "do_not_disturb_pct": percentages["do_not_disturb"],
                "unknown_pct": percentages["unknown"],
                "persuadables_count": counts["persuadables"],
                "sure_things_count": counts["sure_things"],
                "lost_causes_count": counts["lost_causes"],
                "do_not_disturb_count": counts["do_not_disturb"],
                "unknown_count": counts["unknown"],
                "segment_estimation_method": "Rule-based deterministic segmentation from industry, campaign type, audience specificity, channel specificity, and compliance sensitivity.",
                "segment_confidence": segment_confidence,
                "segment_rationale": segment_rationale,
            }
        )

        combo = (str(input_row["industry"]), str(input_row["campaign_type"]))
        should_create_history = index % 3 != 0 and combo not in HISTORY_EXCLUDED_COMBOS
        if should_create_history:
            historical_rows.append(
                build_historical_row(
                    historical_campaign_id=f"HIST_{historical_counter:04d}",
                    input_row=input_row,
                    source_row=brief_row,
                    metadata=metadata,
                    rng=rng,
                )
            )
            historical_counter += 1

    exact_history_names = {str(row["campaign_name"]) for row in historical_rows}
    history_combos = {(str(row["industry"]), str(row["campaign_type"])) for row in historical_rows}
    for input_row in simulation_rows:
        mode, confidence = assign_mode_and_confidence(
            input_row,
            metadata_by_campaign[str(input_row["campaign_id"])],
            exact_history_names,
            history_combos,
        )
        input_row["simulation_mode"] = mode
        input_row["confidence_level"] = confidence

    sim_path = output_dir / SIM_INPUTS_PATH.name
    hist_path = output_dir / HISTORICAL_RESULTS_PATH.name
    seg_path = output_dir / SEGMENTS_PATH.name

    write_rows(sim_path, SIMULATION_INPUT_COLUMNS, simulation_rows)
    write_rows(hist_path, HISTORICAL_RESULTS_COLUMNS, historical_rows)
    write_rows(seg_path, SEGMENT_COLUMNS, segment_rows)

    print(f"Source rows: {len(brief_rows)}")
    print(f"Simulation input rows: {len(simulation_rows)} -> {sim_path}")
    print(f"Historical benchmark rows: {len(historical_rows)} -> {hist_path}")
    print(f"Audience segment rows: {len(segment_rows)} -> {seg_path}")

    print("Sample simulation rows:")
    for sample in simulation_rows[:2]:
        print(json.dumps(sample, indent=2))

    print("Sample segment rows:")
    for sample in segment_rows[:2]:
        print(json.dumps(sample, indent=2))

    return {
        "campaign_simulation_inputs": sim_path,
        "historical_campaign_results": hist_path,
        "campaign_uplift_segments": seg_path,
    }


def main() -> None:
    generate_simulation_data()


if __name__ == "__main__":
    main()