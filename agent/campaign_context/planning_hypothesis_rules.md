# Planning Hypothesis Rules

## Purpose

Every major stage of the Campaign Readiness workflow should produce a planning hypothesis. This makes the AI's reasoning transparent and gives the campaign manager explicit control over assumptions.

## Hypothesis Schema

Every hypothesis must include:

```json
{
  "planning_hypothesis": {
    "statement": "A clear, falsifiable interpretation of the brief",
    "evidence": ["List of specific brief elements supporting this interpretation"],
    "risk_if_wrong": "What happens if this interpretation is incorrect",
    "validation_needed": ["Specific actions to confirm or refute"],
    "confidence": "High | Medium | Low",
    "manager_action_required": true | false
  }
}
```

## When to Generate Hypotheses

- **Brief Parsing** — Hypothesis about campaign type and primary intent
- **Gap Detection** — Hypothesis about why gaps exist (intentional vs. oversight)
- **Ambiguity Resolution** — Hypothesis about likely answers to clarification questions
- **Channel Strategy** — Hypothesis about optimal channel mix
- **Simulation** — Hypothesis about which factors will most impact performance

## Hypothesis Quality Rules

1. Statement must be specific and falsifiable
2. Evidence must reference specific brief content
3. Risk must describe a concrete negative outcome
4. Validation must be actionable (question to ask, data to check)
5. Confidence must be justified

## Confidence Calibration

| Confidence | Criteria |
|-----------|----------|
| High | Multiple evidence points, consistent with common patterns, low ambiguity |
| Medium | Some evidence, plausible interpretation, but alternatives exist |
| Low | Minimal evidence, significant ambiguity, multiple valid interpretations |

## Manager Action Triggers

Set `manager_action_required: true` when:
- Confidence is Low
- Risk-if-wrong has significant budget or legal implications
- Multiple equally valid interpretations exist
- The hypothesis contradicts explicit brief content
- Industry-specific nuance may apply

## Anti-Patterns

- Do NOT generate hypotheses that are unfalsifiable ("this is a good campaign")
- Do NOT generate hypotheses without evidence
- Do NOT mark everything as requiring manager action (creates fatigue)
- Do NOT present hypotheses as facts
