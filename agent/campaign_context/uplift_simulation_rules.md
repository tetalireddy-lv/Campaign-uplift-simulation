# Market Uplift Simulation Rules

## Purpose

The uplift simulation estimates the potential performance improvement between the current brief state and an optimized execution plan. It does NOT predict actual outcomes — it provides scenario-based ranges to help managers make informed decisions.

## Simulation Scenarios

### Scenario 1: Current Brief (As-Is)
- What happens if the campaign launches with the brief as written?
- Accounts for gaps, vagueness, and missing elements
- Applies penalty factors for identified risks

### Scenario 2: Clarified Plan
- What happens if all ambiguities are resolved and gaps filled?
- Assumes manager answers are incorporated
- Uses approved assumptions

### Scenario 3: Optimized Plan
- What happens with optimized channel mix, timing, and targeting?
- Represents the best realistic outcome given constraints
- Includes recommendations for improvement

## Uplift Factors

| Factor | Impact on Uplift | Weight |
|--------|-----------------|--------|
| Audience specificity | High | 0.20 |
| Channel-audience fit | High | 0.20 |
| Message clarity | Medium | 0.15 |
| Budget adequacy | Medium | 0.15 |
| Timeline realism | Medium | 0.10 |
| KPI measurement quality | Low-Medium | 0.10 |
| Compliance readiness | Low | 0.05 |
| Asset completeness | Low | 0.05 |

## Confidence Levels

| Level | Range Width | When Used |
|-------|------------|-----------|
| High | ±10% | All data present, proven channel, known audience |
| Medium | ±25% | Some assumptions, new channel or segment |
| Low | ±50% | Many unknowns, unproven approach, limited data |

## Simulation Output Schema

```json
{
  "scenarios": [
    {
      "name": "Current Brief",
      "estimated_performance": "range",
      "confidence": "level",
      "key_risks": ["list"],
      "blockers": ["list"]
    }
  ],
  "uplift_range": {
    "min": "percentage",
    "max": "percentage",
    "most_likely": "percentage"
  },
  "assumptions_used": ["list"],
  "manager_actions_to_improve": ["list"]
}
```

## Rules

1. Never present a single-point estimate — always a range
2. Always state assumptions explicitly
3. Always show confidence level
4. Always list what could improve the estimate
5. Never imply guaranteed outcomes
6. Simulation is advisory, not predictive
