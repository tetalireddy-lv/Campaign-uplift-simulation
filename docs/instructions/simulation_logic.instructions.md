# Simulation Logic Instructions

## Uplift Calculation

The simulation uses a weighted factor model:

| Factor | Weight |
|--------|--------|
| Audience specificity | 0.20 |
| Channel-audience fit | 0.20 |
| Message clarity | 0.15 |
| Budget adequacy | 0.15 |
| Timeline realism | 0.10 |
| KPI measurement quality | 0.10 |
| Compliance readiness | 0.05 |
| Asset completeness | 0.05 |

## Three Scenarios

1. **As-Is** — Brief launched without changes (applies penalty for gaps)
2. **Clarified** — All gaps resolved, assumptions approved
3. **Optimized** — Best-case with channel optimization

## Rules

- Never present single-point estimates — always ranges
- Always state confidence level explicitly
- Always show what assumptions the estimate depends on
- Never imply guaranteed outcomes
- Simulation is advisory, not predictive
- Manager actions to improve should be concrete and actionable

## Deterministic Scoring

The deterministic portion:
```
base_score = readiness_score
gap_penalty = critical_gaps * 10 + high_gaps * 5
uplift_potential = gap_count * 5 (capped at 50)
```

LLM contextualizes these numbers with qualitative reasoning about the specific campaign.
