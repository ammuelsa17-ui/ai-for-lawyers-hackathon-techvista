# write-to-cms

## Purpose
Commit an attorney-approved case management action (calendar task, docket entry, document filing metadata, status update) to the CMS adapter and record an immutable audit log.

## Input
```json
{
  "matter_id": "str",
  "action_type": "CREATE_TASK" | "UPDATE_STATUS" | "DOCKET_DOCUMENT",
  "payload": {
    "title": "str",
    "due_date": "YYYY-MM-DD",
    "rule_reference": "str",
    "source_doc_id": "str",
    "source_chunk_id": "str"
  },
  "approved_by": "attorney_username"
}
```

## Output
```json
{
  "status": "committed" | "rejected",
  "action_id": "str",
  "cms_task_id": "str",
  "audit_log_id": "str",
  "timestamp": "2026-11-06T12:00:00Z"
}
```

## Rules
- Reject unconditionally if `approved_by` is absent, null, or empty string.
- All writes must execute through `app/cms/adapter.py`.
- Every committed write must produce a persistent, traceable audit log record with timestamps and user identifiers.
- On CMS adapter communication failure, raise an explicit error and do not corrupt the local audit trail.
