# Tool Design Instructions

## Tool Structure

Every tool in `tools/` should follow this pattern:

```python
"""<Tool Name> — <One-line purpose>."""
from __future__ import annotations

from workflow.llm_utils import call_llm_json
from workflow.prompt_renderer import render_prompt


def tool_function(input_arg: type) -> dict:
    """Docstring with clear Args and Returns."""
    prompt = render_prompt("stage/template.j2", **kwargs)
    return call_llm_json(prompt)
```

## Rules

1. **One primary function per tool** — Keep tools focused
2. **Deterministic logic in separate functions** — Scoring, validation, formatting
3. **Return structured JSON** — Never return raw text
4. **Include `if __name__ == "__main__"` block** — For standalone testing
5. **Type hints on all public functions**
6. **Docstrings with Args/Returns on all public functions**

## Deterministic vs. LLM Logic

| Put in Python | Put in LLM Prompt |
|--------------|-------------------|
| Score calculation | Brief interpretation |
| Schema validation | Gap reasoning |
| Routing conditions | Question generation |
| JSON formatting | Plan writing |
| Audit logging | QA explanation |

## Testing

- Each tool should be testable with a mock LLM response
- Deterministic functions should have unit tests
- Integration tests should verify prompt rendering
