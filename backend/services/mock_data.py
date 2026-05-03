"""Mock fallback data for all workflow steps — used when LLM/API key is unavailable."""
from __future__ import annotations


MOCK_STRUCTURED_BRIEF = {
    "campaign_name": "Q3 Enterprise Trial Conversion",
    "business_objective": "Convert 200 enterprise trial accounts to paid subscriptions by end of Q3 2026",
    "target_audience": {
        "description": "Enterprise IT decision-makers currently in 14-day trial",
        "company_size": "500+",
        "demographics": "B2B, senior technical buyers"
    },
    "key_message": "Your team is already seeing results — lock in your progress before trial ends",
    "channels": ["Email", "In-App Messaging", "LinkedIn Ads"],
    "budget": {"total": 85000, "currency": "USD", "breakdown": {"email": 15000, "in_app": 20000, "linkedin": 50000}},
    "timeline": {"start": "2026-06-01", "end": "2026-08-31", "duration_weeks": 13},
    "success_metrics": {"primary": "Trial-to-paid conversion rate", "target": "40%", "baseline": "22%"},
    "constraints": ["No discount offers without VP approval", "Must comply with enterprise data handling policy"],
    "brand_voice": "Professional, data-driven, achievement-focused",
    "competitive_context": "Enterprise SaaS market with high trial abandonment rates",
    "planning_hypothesis": {
        "what_ai_believes": "High-intent trial users can be converted with urgency-driven messaging highlighting ROI already achieved",
        "evidence_from_brief": "14-day trial period, enterprise audience, existing usage data available",
        "risk_if_wrong": "Urgency messaging may feel pushy to enterprise buyers who prefer consultative sales",
        "validation_needed": "Confirm whether usage data can be personalized per account",
        "manager_action_required": "Approve personalization strategy and confirm VP availability for discount approval workflow"
    }
}

MOCK_CAMPAIGN_INTENT = {
    "primary_intent": "Trial Conversion",
    "campaign_type": "B2B Nurture",
    "funnel_stage": "Consideration → Decision",
    "urgency_level": "High",
    "personalization_potential": "High",
    "recommended_approach": "Multi-touch urgency sequence with ROI proof points"
}

MOCK_GAP_REPORT = {
    "readiness_score": 72,
    "overall_assessment": "Brief is moderately complete. Key gaps in personalization strategy and legal approval workflow.",
    "gaps": [
        {"field": "Personalization Strategy", "severity": "high", "description": "No guidance on how to segment or personalize messages per account", "recommendation": "Define segmentation tiers based on usage depth"},
        {"field": "Legal Approval Process", "severity": "medium", "description": "VP approval for discounts is mentioned but process is undefined", "recommendation": "Document approval SLA and escalation path"},
        {"field": "Creative Assets", "severity": "medium", "description": "No creative brief or asset specifications provided", "recommendation": "Align on email templates and LinkedIn ad formats"},
        {"field": "Suppression List", "severity": "low", "description": "No mention of contacts to exclude from campaign", "recommendation": "Define opt-out and competitor employee suppression"}
    ],
    "strengths": ["Clear business objective with quantified target", "Budget allocated across channels", "Specific timeline defined"],
    "planning_hypothesis": {
        "what_ai_believes": "The 18% conversion lift target (22% → 40%) is achievable but requires strong personalization",
        "evidence_from_brief": "Enterprise trials with active usage data show higher conversion potential",
        "risk_if_wrong": "Generic messaging may not move enterprise buyers; lift could be 5-10% instead",
        "validation_needed": "Confirm CRM integration to access per-account usage metrics",
        "manager_action_required": "Confirm data availability for personalization before plan finalizes"
    }
}

MOCK_COMPLIANCE_REPORT = {
    "overall_risk": "Medium",
    "risks": [
        {"category": "Data Privacy", "severity": "high", "description": "Enterprise data handling policy compliance required — GDPR and CCPA implications for targeting", "mitigation": "Legal review of LinkedIn targeting parameters and email data sources"},
        {"category": "Approval Workflow", "severity": "medium", "description": "Discount offers require VP sign-off — no SLA defined", "mitigation": "Establish 48-hour approval SLA and backup approver"},
        {"category": "Brand Compliance", "severity": "low", "description": "No brand guidelines referenced for ad creative", "mitigation": "Confirm brand team review step in asset checklist"}
    ],
    "compliance_checklist": ["GDPR consent validation for EU trial accounts", "CAN-SPAM compliance for email sequences", "LinkedIn ad policy review for enterprise targeting"],
    "planning_hypothesis": {
        "what_ai_believes": "Data privacy compliance is the highest risk and must be resolved before LinkedIn targeting is configured",
        "evidence_from_brief": "Enterprise data handling policy constraint is explicitly called out",
        "risk_if_wrong": "Campaign could be halted mid-flight by legal team",
        "validation_needed": "Legal team review of targeting strategy",
        "manager_action_required": "Send to legal review before LinkedIn campaign setup begins"
    }
}

MOCK_KPI_REPORT = {
    "primary_kpi": {"metric": "Trial-to-Paid Conversion Rate", "target": "40%", "baseline": "22%", "lift_required": "18pp", "measurability": "High"},
    "secondary_kpis": [
        {"metric": "Email Open Rate", "target": "35%", "baseline": "22%", "measurability": "High"},
        {"metric": "LinkedIn CTR", "target": "2.5%", "baseline": "0.8%", "measurability": "High"},
        {"metric": "In-App Engagement Rate", "target": "60%", "baseline": "45%", "measurability": "Medium"}
    ],
    "measurement_gaps": ["No attribution model defined for multi-touch journey", "No holdout group planned for uplift measurement"],
    "tracking_readiness": "Partial — primary KPI is well-defined but attribution framework is missing",
    "planning_hypothesis": {
        "what_ai_believes": "The 40% conversion target is aggressive but feasible with personalized in-app nudges as the primary driver",
        "evidence_from_brief": "In-app messaging typically outperforms email for product-led conversion",
        "risk_if_wrong": "Without holdout group, true campaign uplift cannot be measured",
        "validation_needed": "Confirm analytics team can set up holdout measurement",
        "manager_action_required": "Approve KPI framework and confirm attribution model before launch"
    }
}

MOCK_CLARIFICATION_QUESTIONS = [
    {"id": "q1", "question": "Can we access per-account usage data from the CRM to personalize messaging?", "category": "Data & Personalization", "priority": "critical", "impact": "Determines whether we can run personalized vs generic sequences"},
    {"id": "q2", "question": "What is the VP discount approval SLA? Who is the backup approver?", "category": "Approval Workflow", "priority": "high", "impact": "Required before any discount-bearing emails are sent"},
    {"id": "q3", "question": "Are there specific trial accounts that should be excluded from this campaign?", "category": "Audience", "priority": "high", "impact": "Prevents messaging accounts already in sales conversations"},
    {"id": "q4", "question": "Does the enterprise data policy restrict LinkedIn audience matching using company email domains?", "category": "Compliance", "priority": "high", "impact": "May require alternative LinkedIn targeting approach"},
    {"id": "q5", "question": "What is the fallback plan if trial-to-paid conversion rate is below 30% at the 6-week mark?", "category": "Risk Management", "priority": "medium", "impact": "Ensures contingency planning is in place"}
]

MOCK_ASSUMPTIONS = [
    {"id": "a1", "assumption": "CRM integration is available to pull per-account feature usage data", "confidence": "Medium", "source": "Inferred from 'Enterprise IT' audience with existing trial data", "if_wrong": "Personalization cannot be executed; revert to segment-level messaging"},
    {"id": "a2", "assumption": "VP approval for discounts can be obtained within 48 hours of request", "confidence": "Low", "source": "Standard enterprise approval workflow assumption", "if_wrong": "Discount-triggered emails cannot be included in automated sequences"},
    {"id": "a3", "assumption": "LinkedIn targeting will use job title + company size filters, not email domain matching", "confidence": "High", "source": "Standard B2B LinkedIn campaign approach for enterprise audience", "if_wrong": "Reach may be lower; CPL will increase"},
    {"id": "a4", "assumption": "Email sequences will run 3 touches over 10 days with urgency escalation", "confidence": "Medium", "source": "Best practice for trial conversion email programs", "if_wrong": "Frequency may need adjustment based on engagement data mid-campaign"}
]

MOCK_EXECUTION_PLAN = {
    "campaign_overview": "Multi-channel enterprise trial conversion campaign running June-August 2026",
    "strategy_summary": "Personalized urgency-driven sequences across Email, In-App, and LinkedIn with ROI-proof messaging",
    "phases": [
        {"phase": 1, "name": "Setup & Launch", "weeks": "1-2", "activities": ["CRM data pull and segmentation", "Email template creation", "LinkedIn campaign setup", "Legal review completion"], "owner": "Marketing Ops"},
        {"phase": 2, "name": "Active Conversion Push", "weeks": "3-10", "activities": ["3-touch email sequence per account tier", "In-app notification triggers", "LinkedIn retargeting for non-openers", "Weekly optimization reviews"], "owner": "Campaign Manager"},
        {"phase": 3, "name": "Final Push & Wrap", "weeks": "11-13", "activities": ["Urgency escalation messaging", "Personal outreach for high-value accounts", "Conversion reporting", "Handoff to CS for converted accounts"], "owner": "Campaign Manager + Sales"}
    ],
    "channel_mix": {"email": "35%", "in_app": "40%", "linkedin": "25%"},
    "budget_allocation": {"email": 15000, "in_app": 20000, "linkedin": 50000},
    "planning_hypothesis": {
        "what_ai_believes": "In-App messaging will be the primary conversion driver; Email provides reach; LinkedIn handles re-engagement",
        "evidence_from_brief": "In-app has highest engagement baseline (45%) and direct path to conversion action",
        "risk_if_wrong": "If in-app notifications are ignored, LinkedIn retargeting budget may need reallocation",
        "validation_needed": "Confirm in-app notification opt-in rates for trial accounts",
        "manager_action_required": "Approve channel budget split and confirm in-app notification permissions"
    }
}

MOCK_CHANNEL_STRATEGY = {
    "channels": [
        {"channel": "Email", "budget": 15000, "role": "Primary awareness and urgency driver", "tactics": ["3-touch sequence", "ROI proof points", "Trial expiry countdown"], "kpis": ["Open rate 35%", "CTR 8%"], "cadence": "Day 1, Day 5, Day 10"},
        {"channel": "In-App Messaging", "budget": 20000, "role": "Direct conversion trigger", "tactics": ["Feature adoption nudges", "Upgrade CTA at key usage moments", "Progress celebration messages"], "kpis": ["Engagement rate 60%", "Upgrade click rate 15%"], "cadence": "Triggered by usage events"},
        {"channel": "LinkedIn Ads", "budget": 50000, "role": "Re-engagement and social proof", "tactics": ["Sponsored content with case studies", "Retargeting non-openers", "Company page followers targeting"], "kpis": ["CTR 2.5%", "CPL $125"], "cadence": "Continuous, optimized weekly"}
    ]
}

MOCK_MEASUREMENT_PLAN = {
    "primary_kpi": "Trial-to-paid conversion rate",
    "baseline": "22%",
    "target": "40%",
    "measurement_framework": "Weekly cohort tracking with a 10% holdout group and blended attribution review.",
    "measurement_window": "2026-06-01 to 2026-08-31",
    "reporting_cadence": "Weekly with mid-flight checkpoint",
    "data_sources": ["CRM / CDP", "Marketing automation platform", "Ad platform analytics", "Campaign reporting dashboard"],
    "control_strategy": "Matched audience holdout",
    "success_thresholds": {"minimum_success": "22%", "target_success": "40%"},
    "notes": [
        "Keep KPI definitions aligned across simulation, QA, and handoff outputs.",
        "Validate holdout setup before launch."
    ],
    "owner": "Campaign Manager + Analytics",
}

MOCK_SIMULATION_REPORT = {
    "simulation_mode": "Similar-campaign benchmark",
    "confidence_level": "Medium",
    "primary_kpi": "Trial-to-paid conversion rate",
    "baseline_kpi_value": 22.0,
    "target_kpi_value": 40.0,
    "expected_kpi_value": 33.6,
    "market_uplift_percent": 52.7,
    "scenario_results": [
        {
            "scenario": "Current Brief As-Is",
            "expected_kpi_value": 29.4,
            "market_uplift_percent": 33.6,
            "confidence": "Low",
            "reason": "Audience targeting and measurement setup need to be tightened before launch."
        },
        {
            "scenario": "Clarified Plan",
            "expected_kpi_value": 33.6,
            "market_uplift_percent": 52.7,
            "confidence": "Medium",
            "reason": "Budget, channel roles, and KPI definitions are clearer."
        },
        {
            "scenario": "Optimized Plan",
            "expected_kpi_value": 37.2,
            "market_uplift_percent": 69.1,
            "confidence": "Medium-High",
            "reason": "Audience, CTA, and measurement plan are aligned across the campaign."
        }
    ],
    "scenarios": [
        {
            "scenario": "Current Brief As-Is",
            "expected_kpi_value": 29.4,
            "market_uplift_percent": 33.6,
            "confidence": "Low",
            "reason": "Audience targeting and measurement setup need to be tightened before launch."
        },
        {
            "scenario": "Clarified Plan",
            "expected_kpi_value": 33.6,
            "market_uplift_percent": 52.7,
            "confidence": "Medium",
            "reason": "Budget, channel roles, and KPI definitions are clearer."
        },
        {
            "scenario": "Optimized Plan",
            "expected_kpi_value": 37.2,
            "market_uplift_percent": 69.1,
            "confidence": "Medium-High",
            "reason": "Audience, CTA, and measurement plan are aligned across the campaign."
        }
    ],
    "audience_uplift_mix": {
        "persuadables": {"pct": 34, "count": 3400, "explanation": "Likely to convert because of the campaign."},
        "sure_things": {"pct": 24, "count": 2400, "explanation": "Likely to convert even without the campaign."},
        "lost_causes": {"pct": 22, "count": 2200, "explanation": "Unlikely to convert even with the campaign."},
        "do_not_disturb": {"pct": 12, "count": 1200, "explanation": "May respond negatively or create fatigue or cannibalization risk."},
        "unknown": {"pct": 8, "count": 800, "explanation": "Not enough data to classify confidently."}
    },
    "assumptions_used": [
        {"field": "Budget", "value": "$85,000", "source": "Provided in brief", "editable_by_manager": True},
        {"field": "Holdout strategy", "value": "10% audience holdout", "source": "Assumed", "editable_by_manager": True}
    ],
    "uplift_drivers": ["Audience specificity", "Channel-objective fit", "CTA alignment", "Measurement plan clarity"],
    "uplift_blockers": ["CRM data quality risk", "VP approval dependency for discount offers"],
    "manager_editable_fields": [
        "audience_size",
        "budget_numeric",
        "baseline_kpi_value",
        "target_kpi_value",
        "persuadables_pct",
        "sure_things_pct",
        "lost_causes_pct",
        "do_not_disturb_pct",
        "unknown_pct"
    ],
    "warning": "This is a scenario estimate, not a guaranteed forecast. Assumed values should be reviewed by the campaign manager.",
    "expected_value": 33.6,
    "expected_campaign_revenue": 633000,
    "roi": 644.7,
    "risk_factors": ["CRM data quality risk", "VP approval dependency for discount offers"],
    "recommendation": "Proceed with the clarified plan and validate the holdout setup before launch."
}

MOCK_QA_REPORT = {
    "alignment_score": 87,
    "overall_verdict": "Plan is well-aligned with brief. Two minor gaps to resolve before launch.",
    "aligned_items": [
        "Budget allocation matches channel strategy",
        "Timeline is feasible for Q3 execution",
        "Primary KPI is consistently measured across all plan sections",
        "Compliance risks are acknowledged in execution plan"
    ],
    "gaps": [
        {"issue": "Holdout group not defined in execution plan", "severity": "medium", "recommendation": "Add 10% control group to measure true uplift"},
        {"issue": "Asset creation timeline not included in phase 1", "severity": "low", "recommendation": "Add creative production sprint to week 1-2 activities"}
    ],
    "critical_misalignments": [],
    "planning_hypothesis": {
        "what_ai_believes": "The plan is launch-ready pending the two gap resolutions above",
        "evidence_from_brief": "All major brief requirements are reflected in the execution plan",
        "risk_if_wrong": "Missing holdout group means ROI cannot be proven for future budget requests",
        "validation_needed": "Analytics team confirmation of holdout setup feasibility",
        "manager_action_required": "Approve QA findings and authorize handoff packet generation"
    }
}

MOCK_HANDOFF_PACKET = {
    "campaign_name": "Q3 Enterprise Trial Conversion",
    "launch_date": "2026-06-01",
    "status": "READY FOR APPROVAL — NOT LAUNCHED",
    "executive_summary": "Multi-channel B2B campaign targeting 500+ enterprise trial accounts. The benchmark-backed estimate moves trial-to-paid conversion from 22% to 33.6% with 52.7% uplift under the clarified plan.",
    "stakeholder_sections": {
        "for_marketing_ops": ["CRM data pull spec: active trials >3 days usage, company_size>500", "Email template brief attached", "LinkedIn campaign setup checklist enclosed"],
        "for_legal": ["LinkedIn targeting parameters for review", "GDPR compliance checklist", "Email data source documentation"],
        "for_sales": ["List of top 50 high-value trial accounts for personal outreach in Phase 3", "Handoff SLA: converted accounts within 24 hours"],
        "for_analytics": ["KPI tracking dashboard requirements", "Holdout group setup: 10% of eligible accounts", "Attribution model: first-touch + last-touch blended"]
    },
    "approved_assumptions": [],
    "risk_register": ["Data privacy compliance (High) — Legal review required", "VP approval speed for discounts (Medium) — SLA needed", "CRM data quality (Medium) — Validate before launch"],
    "next_steps": [
        "Manager approves this handoff packet",
        "Legal reviews compliance section (ETA: 3 business days)",
        "Marketing Ops begins phase 1 setup",
        "Campaign Manager schedules kickoff meeting with all stakeholders"
    ],
    "important_notice": "This is a scenario estimate, not a guaranteed forecast. Assumed values should be reviewed by the campaign manager.",
    "market_uplift_summary": {
        "simulation_mode": "Similar-campaign benchmark",
        "confidence_level": "Medium",
        "baseline_kpi": {"name": "Trial-to-paid conversion rate", "value": 22.0},
        "target_kpi": 40.0,
        "expected_kpi": 33.6,
        "market_uplift_percent": 52.7,
        "audience_uplift_mix": {
            "persuadables": {"pct": 34, "count": 3400, "explanation": "Likely to convert because of the campaign."},
            "sure_things": {"pct": 24, "count": 2400, "explanation": "Likely to convert even without the campaign."},
            "lost_causes": {"pct": 22, "count": 2200, "explanation": "Unlikely to convert even with the campaign."},
            "do_not_disturb": {"pct": 12, "count": 1200, "explanation": "May respond negatively or create fatigue or cannibalization risk."},
            "unknown": {"pct": 8, "count": 800, "explanation": "Not enough data to classify confidently."}
        },
        "top_uplift_drivers": ["Audience specificity", "Channel-objective fit", "CTA alignment"],
        "top_uplift_blockers": ["CRM data quality risk", "VP approval dependency for discount offers"],
        "warning": "This is a scenario estimate, not a guaranteed forecast. Assumed values should be reviewed by the campaign manager."
    }
}
