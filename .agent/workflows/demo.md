# Workflow: PS-01 Demo Storyboard (demo.md)

## Objective
Replay the exact PS-01 demonstration sequence end-to-end to validate that CasePilot fulfills all required verbs and product tiers.

## Storyboard Sequence

### Step 1: Matter Dashboard & Deadline Overview
- Launch application via `docker compose up` or local runner.
- Open Streamlit dashboard at `http://localhost:8501`.
- View matters list with status, next deadline, and overdue items highlighted.

### Step 2: Document Ingestion & Classification
- Navigate to Document Filing tab.
- Upload synthetic case document (e.g. `summons_and_complaint.txt` or `deposition_witness_a.txt`).
- Observe automatic document classification (e.g., Pleading, Motion, Discovery) and suggested folder assignment.

### Step 3: Deadline Extraction & Human Approval Gate
- Trigger deadline extraction on the ingested document.
- Observe extracted date, legal rule reference, and citation source chunk.
- Verify the action sits in **Pending Approval** queue (no automatic write-back).
- Provide attorney identifier (`approved_by: "attorney_jane"`) and click **Approve & Sync to CMS**.
- Confirm task appears in the mock CMS calendar and audit log.

### Step 4: Matter Change Feed
- Open the Matter Change Feed tab.
- Observe real-time audit ledger:
  - "New document ingested and classified"
  - "New deadline extracted and approved"
  - "Task written back to CMS by attorney_jane"

### Step 5: Cited Case-File Q&A
- Navigate to Case Q&A tab.
- Ask a factual inquiry (e.g. "When was the initial complaint served and what relief was demanded?").
- Verify that every answer contains structured citations with `doc_id`, `chunk_id`, and `page`.

### Step 6: Contradiction / Anomaly Detection
- Upload conflicting evidence document (e.g. `deposition_witness_b.txt` contradicting dates/statements).
- Trigger contradiction analysis.
- Verify anomaly flag highlights conflicting statements with dual citations comparing both source chunks.
