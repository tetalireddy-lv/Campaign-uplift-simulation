from __future__ import annotations

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent.data.scripts.generate_simulation_data import (
    HISTORICAL_RESULTS_COLUMNS,
    SEGMENT_COLUMNS,
    SIMULATION_INPUT_COLUMNS,
    generate_simulation_data,
)
from agent.tools.campaign_uplift_simulator_tool import simulate_uplift


BRIEF_COLUMNS = [
    "Campaign Name",
    "Business Objective",
    "Target Audience",
    "Key Message",
    "Channels",
    "Budget",
    "Timeline",
    "Success Metrics",
    "Constraints / Brand Notes",
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class SimulationDataGenerationTests(unittest.TestCase):
    def test_generate_simulation_data_creates_all_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            briefs_path = temp_path / "campaign_briefs.csv"
            write_csv(
                briefs_path,
                BRIEF_COLUMNS,
                [
                    {
                        "Campaign Name": "NorthBridge Bank Fall - Launch",
                        "Business Objective": "Build awareness and momentum",
                        "Target Audience": "lapsed buyers",
                        "Key Message": "Meet Pinecrest Trust: everything you loved, reimagined.",
                        "Channels": "Programmatic, Paid Search, Direct Mail",
                        "Budget": "$66,000 excl. production",
                        "Timeline": "summer push",
                        "Success Metrics": "New sign-ups: target 7,193 over the campaign flight; CPA <= $200.",
                        "Constraints / Brand Notes": "All offers must include APR/APY disclosures and FDIC member language.",
                    },
                    {
                        "Campaign Name": "MediBridge 2026 - Retention Sprint",
                        "Business Objective": "Drive more revenue from this audience",
                        "Target Audience": "small business owners",
                        "Key Message": "Here's what's new, just for you.",
                        "Channels": "online",
                        "Budget": "$645,000",
                        "Timeline": "Sep 17, 2026 - 2 week flight",
                        "Success Metrics": "ROAS target 3.8",
                        "Constraints / Brand Notes": "All medical claims must be reviewed by Medical Legal Review (MLR) before launch.",
                    },
                ],
            )

            with contextlib.redirect_stdout(io.StringIO()):
                paths = generate_simulation_data(source_path=briefs_path, output_dir=temp_path, seed=20260503)

            self.assertTrue(paths["campaign_simulation_inputs"].exists())
            self.assertTrue(paths["historical_campaign_results"].exists())
            self.assertTrue(paths["campaign_uplift_segments"].exists())

    def test_segment_percentages_sum_to_100(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            briefs_path = temp_path / "campaign_briefs.csv"
            write_csv(
                briefs_path,
                BRIEF_COLUMNS,
                [
                    {
                        "Campaign Name": "NorthBridge Bank Fall - Launch",
                        "Business Objective": "Build awareness and momentum",
                        "Target Audience": "lapsed buyers",
                        "Key Message": "Meet Pinecrest Trust: everything you loved, reimagined.",
                        "Channels": "Programmatic, Paid Search, Direct Mail",
                        "Budget": "$66,000 excl. production",
                        "Timeline": "summer push",
                        "Success Metrics": "New sign-ups: target 7,193 over the campaign flight; CPA <= $200.",
                        "Constraints / Brand Notes": "All offers must include APR/APY disclosures and FDIC member language.",
                    }
                ],
            )

            with contextlib.redirect_stdout(io.StringIO()):
                paths = generate_simulation_data(source_path=briefs_path, output_dir=temp_path, seed=20260503)

            with paths["campaign_uplift_segments"].open(newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle))

            pct_sum = sum(
                int(row[column])
                for column in [
                    "persuadables_pct",
                    "sure_things_pct",
                    "lost_causes_pct",
                    "do_not_disturb_pct",
                    "unknown_pct",
                ]
            )
            self.assertEqual(pct_sum, 100)


class MarketUpliftSimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.structured_brief = {
            "campaign_name": "Sample Trial Conversion",
            "business_objective": "Convert active trial users to paid plans",
            "target_audience": "Enterprise trial users with 3+ product sessions",
            "key_message": "Lock in your progress with a paid plan.",
            "channels": ["Email", "LinkedIn Ads"],
            "budget": {"total": 50000, "currency": "USD"},
            "timeline": {"start": "2026-07-01", "end": "2026-08-15"},
            "success_metrics": {"primary": {"metric": "Trial-to-paid conversion rate", "baseline": "14%", "target": "22%"}},
            "constraints": ["GDPR consent required for EU audiences"],
        }
        self.execution_plan = {
            "strategy_summary": "Personalized trial conversion sequence with email and LinkedIn reinforcement.",
            "campaign_overview": "Trial-to-paid conversion push.",
            "channel_mix": {"Email": "55%", "LinkedIn Ads": "45%"},
        }
        self.measurement_plan = {
            "primary_kpi": "Trial-to-paid conversion rate",
            "measurement_framework": "Weekly cohort tracking",
            "data_sources": ["CRM", "Marketing automation platform"],
            "reporting_cadence": "Weekly",
            "control_strategy": "Matched holdout",
        }

    def _write_supporting_files(self, temp_path: Path, historical_rows: list[dict[str, object]]) -> None:
        write_csv(
            temp_path / "campaign_simulation_inputs.csv",
            SIMULATION_INPUT_COLUMNS,
            [
                {
                    "campaign_id": "CMP_0001",
                    "campaign_name": "Sample Trial Conversion",
                    "industry": "B2B SaaS",
                    "campaign_type": "Trial-to-Paid Conversion",
                    "audience_size": 10000,
                    "estimated_reach": 7200,
                    "baseline_kpi_name": "Trial-to-paid conversion rate",
                    "baseline_kpi_value": 14.0,
                    "target_kpi_value": 22.0,
                    "expected_kpi_value": 18.4,
                    "market_uplift_percent": 31.4,
                    "average_order_value": 1200,
                    "baseline_revenue": 1209600,
                    "expected_campaign_revenue": 1589760,
                    "budget_numeric": 50000,
                    "simulation_mode": "Similar-campaign benchmark",
                    "confidence_level": "Medium",
                    "assumptions_used": json.dumps([
                        {"field": "Budget", "value": "$50,000", "source": "Provided in brief", "editable_by_manager": True},
                        {"field": "Audience Size", "value": 10000, "source": "Estimated from CRM-eligible trial pool", "editable_by_manager": True},
                    ]),
                }
            ],
        )
        write_csv(
            temp_path / "campaign_uplift_segments.csv",
            SEGMENT_COLUMNS,
            [
                {
                    "campaign_id": "CMP_0001",
                    "campaign_name": "Sample Trial Conversion",
                    "audience_size": 10000,
                    "persuadables_pct": 34,
                    "sure_things_pct": 26,
                    "lost_causes_pct": 24,
                    "do_not_disturb_pct": 10,
                    "unknown_pct": 6,
                    "persuadables_count": 3400,
                    "sure_things_count": 2600,
                    "lost_causes_count": 2400,
                    "do_not_disturb_count": 1000,
                    "unknown_count": 600,
                    "segment_estimation_method": "Rule-based deterministic segmentation",
                    "segment_confidence": "Medium",
                    "segment_rationale": "Specific lifecycle audience with known channels improves persuadable share.",
                }
            ],
        )
        write_csv(
            temp_path / "historical_campaign_results.csv",
            HISTORICAL_RESULTS_COLUMNS,
            historical_rows,
        )

    def test_market_uplift_simulator_returns_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_supporting_files(
                temp_path,
                historical_rows=[
                    {
                        "historical_campaign_id": "HIST_0001",
                        "campaign_name": "Another Trial Benchmark",
                        "industry": "B2B SaaS",
                        "campaign_type": "Trial-to-Paid Conversion",
                        "audience_type": "Specific",
                        "channels": "Email, LinkedIn Ads",
                        "budget": 48000,
                        "audience_size": 9800,
                        "treated_count": 8000,
                        "control_count": 1800,
                        "treated_conversion_rate": 18.6,
                        "control_conversion_rate": 14.2,
                        "incremental_lift_points": 4.4,
                        "relative_uplift_percent": 31.0,
                        "revenue_per_conversion": 1200,
                        "campaign_revenue": 1572000,
                        "negative_response_rate": 0.8,
                        "unsubscribe_rate": 0.5,
                        "complaint_rate": 0.1,
                        "notes": "Similar benchmark",
                    }
                ],
            )

            result = simulate_uplift(
                self.structured_brief,
                self.execution_plan,
                approved_assumptions=[],
                measurement_plan=self.measurement_plan,
                campaign_id="CMP_0001",
                data_directory=temp_path,
            )

            required_fields = {
                "simulation_mode",
                "confidence_level",
                "primary_kpi",
                "baseline_kpi_value",
                "target_kpi_value",
                "expected_kpi_value",
                "market_uplift_percent",
                "scenario_results",
                "audience_uplift_mix",
                "assumptions_used",
                "uplift_drivers",
                "uplift_blockers",
                "manager_editable_fields",
                "warning",
            }
            self.assertTrue(required_fields.issubset(result.keys()))

    def test_fallback_when_campaign_id_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_supporting_files(temp_path, historical_rows=[])

            result = simulate_uplift(
                self.structured_brief,
                self.execution_plan,
                approved_assumptions=[],
                measurement_plan=self.measurement_plan,
                data_directory=temp_path,
            )

            self.assertEqual(result["campaign_id"], "CMP_0001")
            self.assertEqual(result["primary_kpi"], "Trial-to-paid conversion rate")

    def test_assumption_based_mode_when_no_historical_match_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_supporting_files(
                temp_path,
                historical_rows=[
                    {
                        "historical_campaign_id": "HIST_9999",
                        "campaign_name": "Retail Promo Benchmark",
                        "industry": "E-commerce",
                        "campaign_type": "Seasonal Promotion",
                        "audience_type": "Broad",
                        "channels": "Paid Social",
                        "budget": 30000,
                        "audience_size": 45000,
                        "treated_count": 36000,
                        "control_count": 9000,
                        "treated_conversion_rate": 4.8,
                        "control_conversion_rate": 3.9,
                        "incremental_lift_points": 0.9,
                        "relative_uplift_percent": 23.1,
                        "revenue_per_conversion": 85,
                        "campaign_revenue": 146880,
                        "negative_response_rate": 1.1,
                        "unsubscribe_rate": 0.7,
                        "complaint_rate": 0.1,
                        "notes": "Non-matching combo",
                    }
                ],
            )

            result = simulate_uplift(
                self.structured_brief,
                self.execution_plan,
                approved_assumptions=[],
                measurement_plan=self.measurement_plan,
                campaign_id="CMP_0001",
                data_directory=temp_path,
            )

            self.assertEqual(result["simulation_mode"], "Assumption-based")

    def test_similar_campaign_benchmark_mode_when_history_matches_combo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._write_supporting_files(
                temp_path,
                historical_rows=[
                    {
                        "historical_campaign_id": "HIST_0002",
                        "campaign_name": "Benchmark Trial Conversion",
                        "industry": "B2B SaaS",
                        "campaign_type": "Trial-to-Paid Conversion",
                        "audience_type": "Specific",
                        "channels": "Email, LinkedIn Ads",
                        "budget": 51000,
                        "audience_size": 10200,
                        "treated_count": 8100,
                        "control_count": 2100,
                        "treated_conversion_rate": 18.3,
                        "control_conversion_rate": 14.0,
                        "incremental_lift_points": 4.3,
                        "relative_uplift_percent": 30.7,
                        "revenue_per_conversion": 1200,
                        "campaign_revenue": 1584000,
                        "negative_response_rate": 0.7,
                        "unsubscribe_rate": 0.4,
                        "complaint_rate": 0.1,
                        "notes": "Matching combo",
                    }
                ],
            )

            result = simulate_uplift(
                self.structured_brief,
                self.execution_plan,
                approved_assumptions=[],
                measurement_plan=self.measurement_plan,
                campaign_id="CMP_0001",
                data_directory=temp_path,
            )

            self.assertEqual(result["simulation_mode"], "Similar-campaign benchmark")


if __name__ == "__main__":
    unittest.main()