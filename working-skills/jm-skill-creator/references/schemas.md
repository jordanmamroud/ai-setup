# JSON Schemas

This document defines the JSON files used by skill-creator's feedback-improve loop.

---

## evals.json

Defines the test cases for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"]
    },
    {
      "id": 2,
      "scope": "structure-recommendations",
      "prompt": "here's my approved intent map — build the campaign structure from it",
      "expected_output": "Structure draft derived from the fixture intent map",
      "files": ["evals/fixtures/structure-recommendations/intent_map.json"]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].scope`: Optional. Names the workflow step or feature this eval targets in isolation. Scoped evals typically reference fixture inputs under `evals/fixtures/<scope>/` (captured from a previous full run or hand-authored)

---

## state.json

Tracks where the eval/improve loop stands. Located at workspace root. Read it when entering the eval workflow; bump `current_iteration` when starting a new iteration.

```json
{
  "current_iteration": 2,
  "criteria_path": "/path/to/skill/evals/criteria.md"
}
```

**Fields:**
- `current_iteration`: The iteration currently in progress (or most recently completed)
- `criteria_path`: Absolute path to the user's judging criteria file (it lives in the skill directory, not the workspace, so relative paths are ambiguous)

---

## eval_metadata.json

Describes one test case within an iteration. Located at `<iteration-dir>/<eval-dir>/eval_metadata.json`. The viewer reads it to show the prompt alongside the outputs.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt"
}
```

---

## feedback.json

Written by the viewer when the user clicks "Submit All Reviews". Located at the workspace root (or downloaded and copied there in headless environments).

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback on a run means the user thought it was fine.
