"""Prompt rendering utilities using Jinja2."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
CONTEXT_DIR = Path(__file__).resolve().parent.parent / "campaign_context"

_env = Environment(
    loader=FileSystemLoader([str(PROMPTS_DIR), str(CONTEXT_DIR)]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _load_context(filename: str) -> str:
    """Load a campaign context markdown file as a string."""
    path = CONTEXT_DIR / filename
    return path.read_text(encoding="utf-8")


# Pre-load all context documents
CAMPAIGN_DOMAIN = _load_context("campaign_domain.md")
BRIEF_SCHEMA = _load_context("brief_schema.md")
CHANNEL_STRATEGY_RULES = _load_context("channel_strategy_rules.md")
COMPLIANCE_BRAND_RULES = _load_context("compliance_brand_rules.md")
KPI_MEASUREMENT_RULES = _load_context("kpi_measurement_rules.md")
UPLIFT_SIMULATION_RULES = _load_context("uplift_simulation_rules.md")
PLANNING_HYPOTHESIS_RULES = _load_context("planning_hypothesis_rules.md")
APPROVAL_WORKFLOW_RULES = _load_context("approval_workflow_rules.md")


def render_prompt(template_path: str, **kwargs) -> str:
    """Render a Jinja2 prompt template with context and variables.

    Args:
        template_path: Relative path within prompts/ (e.g., 'parse_brief/brief_parser.j2')
        **kwargs: Variables to pass into the template

    Returns:
        Rendered prompt string
    """
    # Inject standard context variables
    context = {
        "campaign_domain": CAMPAIGN_DOMAIN,
        "brief_schema": BRIEF_SCHEMA,
        "channel_strategy_rules": CHANNEL_STRATEGY_RULES,
        "compliance_brand_rules": COMPLIANCE_BRAND_RULES,
        "kpi_measurement_rules": KPI_MEASUREMENT_RULES,
        "uplift_simulation_rules": UPLIFT_SIMULATION_RULES,
        "planning_hypothesis_rules": PLANNING_HYPOTHESIS_RULES,
        "approval_workflow_rules": APPROVAL_WORKFLOW_RULES,
    }
    context.update(kwargs)

    template = _env.get_template(template_path)
    return template.render(**context)
