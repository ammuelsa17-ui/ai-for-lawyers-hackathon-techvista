# CasePilot — PS-01: Streamlining Case Management

## One sentence
An AI orchestration layer that automates case management tasks — docketing,
filing, deadline tracking, status updates — inside the case management
systems law firms already use.

## The PS-01 verbs we must satisfy
- Automate case management tasks (deadlines, filing, task creation, status)
- Track matters (status, next deadline, overdue items, what changed)
- Manage efficiently (write-back to CMS, human approval, audit log)

## Product tiers (build in this order)
1. Mock CMS adapter + deadline extraction + task write-back + approval gate
2. Matter dashboard with deadline tracker (upcoming / overdue / done)
3. Document ingestion + auto-classification + auto-filing
4. Change feed ("3 new docs, 1 new deadline, 1 conflict since yesterday")
5. Cited case-file Q&A
6. Contradiction / anomaly flag on new evidence

## Explicitly out of scope
- Voice intake, real client data, billing, multi-CMS live support,
  broad legal research outside the uploaded case file.

## Non-negotiables
- Every AI output cites its source document and chunk/page.
- No write to the CMS adapter without attorney approval.
- Synthetic case data only.
- One-command local demo via Docker Compose.
