# ingest-document

## Purpose
Ingest raw case documents (PDF, TXT, DOCX), extract text with exact page boundaries, generate structured chunks, and index into the matter's ChromaDB collection.

## Input
```json
{
  "matter_id": "str",
  "file_path": "str",
  "file_name": "str"
}
```

## Output
```json
{
  "doc_id": "str",
  "matter_id": "str",
  "total_pages": 4,
  "chunks": [
    {
      "chunk_id": "str",
      "doc_id": "str",
      "page": 1,
      "text": "str",
      "metadata": {
        "file_name": "str",
        "matter_id": "str"
      }
    }
  ]
}
```

## Rules
- Preserve exact page numbers and chunk positions for citation integrity.
- Store chunks into the matter-isolated vector collection (`matter_{matter_id}`).
- Fail cleanly with descriptive error if file format is unsupported or text cannot be extracted.
- Never strip or lose metadata required for `{doc_id, chunk_id, page}` citations.
