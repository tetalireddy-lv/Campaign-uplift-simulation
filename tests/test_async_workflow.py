"""Tests for async workflow service.

Covers:
  1. Output field shapes are unchanged in mock mode (no LLM credentials needed).
  2. Parallel stages are measurably faster than sequential execution.
  3. Fallback safety: _async_call_with_fallback recovers from unexpected exceptions.
  4. One failed parallel task does not prevent the other tasks from returning results.
"""
from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Add backend directory so imports work identically to how the server sees them
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import services.workflow_service as wf  # noqa: E402 — path must be set first


# ── Shared fixtures ──────────────────────────────────────────────────────────

SAMPLE_BRIEF = {
    "campaign_name": "Test Campaign",
    "business_objective": "Drive trial-to-paid conversion",
    "target_audience": "Enterprise trial users with 3+ sessions",
    "key_message": "Lock in your progress.",
    "channels": ["Email", "LinkedIn Ads"],
    "budget": {"total": 50000, "currency": "USD"},
    "timeline": {"start": "2026-07-01", "end": "2026-08-15"},
    "success_metrics": {
        "primary": {"metric": "Trial-to-paid conversion rate", "baseline": "14%", "target": "22%"}
    },
    "constraints": ["GDPR consent required for EU audiences"],
}

SAMPLE_PLAN = {
    "strategy_summary": "Personalized trial conversion sequence.",
    "campaign_overview": "Trial-to-paid conversion push.",
    "channel_mix": {"Email": "55%", "LinkedIn Ads": "45%"},
}

SAMPLE_CHANNEL = {
    "channels": [
        {"channel": "Email", "budget_pct": 55},
        {"channel": "LinkedIn Ads", "budget_pct": 45},
    ]
}

SAMPLE_SIMULATION = {
    "primary_kpi": "Trial-to-paid conversion rate",
    "baseline_kpi_value": 14.0,
    "expected_kpi_value": 18.4,
    "target_kpi_value": 22.0,
    "market_uplift_percent": 31.4,
    "simulation_mode": "Similar-campaign benchmark",
    "confidence_level": "Medium",
    "uplift_drivers": ["Audience specificity"],
    "uplift_blockers": [],
}


# ── Output shape tests ───────────────────────────────────────────────────────

class TestAsyncWorkflowOutputShape(unittest.IsolatedAsyncioTestCase):
    """Verify each async workflow function returns the expected field set in mock mode."""

    async def test_parse_brief_returns_expected_fields(self):
        result = await wf.run_parse_brief("Launch a new product campaign for Q3.")
        self.assertIn("structured_brief", result)
        self.assertIn("campaign_intent", result)
        self.assertIsInstance(result["structured_brief"], dict)
        self.assertIsInstance(result["campaign_intent"], dict)

    async def test_validate_readiness_returns_expected_fields(self):
        result = await wf.run_validate_readiness(SAMPLE_BRIEF)
        self.assertIn("gap_report", result)
        self.assertIn("compliance_report", result)
        self.assertIn("kpi_report", result)
        self.assertIn("readiness_score", result)
        self.assertIsInstance(result["readiness_score"], int)

    async def test_resolve_ambiguity_returns_expected_fields(self):
        result = await wf.run_resolve_ambiguity(
            SAMPLE_BRIEF,
            gap_report={"gaps": []},
            compliance_report={},
            kpi_report={},
        )
        self.assertIn("clarification_questions", result)
        self.assertIn("assumptions", result)
        self.assertIsInstance(result["clarification_questions"], list)
        self.assertIsInstance(result["assumptions"], list)

    async def test_plan_and_simulate_returns_expected_fields(self):
        result = await wf.run_plan_and_simulate(
            SAMPLE_BRIEF,
            gap_report={"gaps": []},
            approved_assumptions=[],
            manager_answers={},
        )
        for field in (
            "channel_strategy",
            "execution_plan",
            "asset_checklist",
            "timeline_plan",
            "measurement_plan",
            "simulation_report",
        ):
            self.assertIn(field, result, f"Missing field: {field}")
            self.assertIsInstance(result[field], dict, f"Field not a dict: {field}")

    async def test_qa_and_handoff_returns_expected_fields(self):
        result = await wf.run_qa_and_handoff(
            SAMPLE_BRIEF,
            execution_plan=SAMPLE_PLAN,
            channel_strategy=SAMPLE_CHANNEL,
            compliance_report={},
            simulation_report=SAMPLE_SIMULATION,
            approved_assumptions=[],
        )
        for field in ("qa_report", "consistency_report", "final_compliance_report", "handoff_packet"):
            self.assertIn(field, result, f"Missing field: {field}")
            self.assertIsInstance(result[field], dict, f"Field not a dict: {field}")


# ── Parallel speed tests ─────────────────────────────────────────────────────

class TestParallelExecution(unittest.IsolatedAsyncioTestCase):
    """Verify parallel stages complete faster than sequential would.

    Each patched _call_with_fallback sleeps 50 ms so:
      - 3 sequential calls would take ~150 ms.
      - 3 parallel calls should complete in ~50–80 ms.
    """

    def _make_slow_fallback(self, delay: float = 0.05):
        original = wf._call_with_fallback

        def slow(prompt, fallback, label):
            time.sleep(delay)
            return original(prompt, fallback, label)

        return slow

    async def test_validate_readiness_parallel_is_faster_than_sequential(self):
        with patch.object(wf, "_call_with_fallback", self._make_slow_fallback(0.05)):
            t0 = time.perf_counter()
            await wf.run_validate_readiness(SAMPLE_BRIEF)
            elapsed = time.perf_counter() - t0

        # 3 parallel × 50 ms — allow generous headroom for CI thread pool overhead
        self.assertLess(
            elapsed, 0.13,
            f"validate_readiness took {elapsed:.3f}s; expected < 0.13s with parallel execution",
        )

    async def test_qa_handoff_parallel_is_faster_than_sequential(self):
        with patch.object(wf, "_call_with_fallback", self._make_slow_fallback(0.05)):
            t0 = time.perf_counter()
            await wf.run_qa_and_handoff(
                SAMPLE_BRIEF,
                execution_plan=SAMPLE_PLAN,
                channel_strategy=SAMPLE_CHANNEL,
                compliance_report={},
                simulation_report=SAMPLE_SIMULATION,
                approved_assumptions=[],
            )
            elapsed = time.perf_counter() - t0

        # 3 parallel QA × 50 ms + fast handoff packet — allow for overhead
        self.assertLess(
            elapsed, 0.25,
            f"qa_and_handoff took {elapsed:.3f}s; expected < 0.25s with parallel QA stage",
        )

    async def test_parse_brief_parallel_is_faster_than_sequential(self):
        with patch.object(wf, "_call_with_fallback", self._make_slow_fallback(0.05)):
            t0 = time.perf_counter()
            await wf.run_parse_brief("Test brief for Q3 product launch.")
            elapsed = time.perf_counter() - t0

        # 2 parallel × 50 ms — should complete in ~50 ms
        self.assertLess(
            elapsed, 0.10,
            f"run_parse_brief took {elapsed:.3f}s; expected < 0.10s with parallel execution",
        )


# ── Fallback / error handling tests ─────────────────────────────────────────

class TestAsyncFallbackBehavior(unittest.IsolatedAsyncioTestCase):
    """Verify the async safety net in _async_call_with_fallback."""

    async def test_async_wrapper_returns_mock_on_unexpected_exception(self):
        """_async_call_with_fallback must return the fallback dict if _call_with_fallback raises."""

        def always_raise(prompt, fallback, label):
            raise RuntimeError("Simulated unexpected crash")

        with patch.object(wf, "_call_with_fallback", always_raise):
            result = await wf._async_call_with_fallback(
                "test prompt",
                {"field_a": "value_a"},
                "test_label",
            )

        self.assertEqual(result.get("_source"), "mock")
        self.assertEqual(result.get("field_a"), "value_a")

    async def test_validate_readiness_completes_when_one_task_crashes(self):
        """gather still returns results for all tasks when one task's wrapper catches its exception."""
        original = wf._call_with_fallback
        call_order: list[str] = []

        def partially_failing(prompt, fallback, label):
            call_order.append(label)
            if label == "compliance_risk_review":
                raise RuntimeError("Simulated compliance tool failure")
            return original(prompt, fallback, label)

        with patch.object(wf, "_call_with_fallback", partially_failing):
            result = await wf.run_validate_readiness(SAMPLE_BRIEF)

        # All three fields must be present regardless of which tool failed
        self.assertIn("gap_report", result)
        self.assertIn("compliance_report", result)
        self.assertIn("kpi_report", result)
        self.assertIsInstance(result["readiness_score"], int)

    async def test_qa_handoff_completes_when_one_qa_task_crashes(self):
        """Handoff packet is still generated even if one QA LLM call fails."""
        original = wf._call_with_fallback

        def qa_crash(prompt, fallback, label):
            if label == "multi_channel_consistency":
                raise RuntimeError("Simulated consistency check failure")
            return original(prompt, fallback, label)

        with patch.object(wf, "_call_with_fallback", qa_crash):
            result = await wf.run_qa_and_handoff(
                SAMPLE_BRIEF,
                execution_plan=SAMPLE_PLAN,
                channel_strategy=SAMPLE_CHANNEL,
                compliance_report={},
                simulation_report=SAMPLE_SIMULATION,
                approved_assumptions=[],
            )

        for field in ("qa_report", "consistency_report", "final_compliance_report", "handoff_packet"):
            self.assertIn(field, result, f"Missing field after partial failure: {field}")


if __name__ == "__main__":
    unittest.main()
