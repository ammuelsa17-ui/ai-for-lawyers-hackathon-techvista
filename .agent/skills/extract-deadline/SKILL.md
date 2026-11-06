# extract-deadline

## Purpose
Given a document's extracted text, propose zero or more case deadlines.

## Input
```json
{
  "doc_id": "str",
  "text": "str",
  "matter_id": "str"
}
```

## Output
```json
[
  {
    "date": "YYYY-MM-DD",
    "rule": "str",
    "trigger_event": "str",
    "confidence": 0.95,
    "source_chunk_id": "str"
  }
]
```

## Rules
- Only propose a deadline if a date AND a trigger event are both present.
- Cite the source chunk for every deadline.
- Return `[]` if no deadline is found. Never guess.
- Deadline math is delegated to `app/legal/deadlines.py`.
- Must never write directly to CMS; output is routed to human review approval queue.
