# classify-document

## Purpose
Classify ingested legal documents into standard litigation categories and suggest matter folder destination.

## Input
```json
{
  "doc_id": "str",
  "matter_id": "str",
  "text": "str"
}
```

## Output
```json
{
  "category": "Pleading" | "Motion" | "Discovery" | "Subpoena" | "Court Order" | "Correspondence" | "Settlement" | "Other",
  "confidence": 0.95,
  "summary": "Brief 1-2 sentence description of document content",
  "suggested_folder": "Pleadings/Complaints",
  "filing_tags": ["initial_pleading", "summons_attached"]
}
```

## Rules
- Fall back to `"Other"` with low confidence if document classification is ambiguous.
- Categorization must guide filing recommendations, but filing actions require attorney confirmation before CMS state changes.
- Never fabricate classification categories outside the standard ontology defined in the system.
