# Workflow: Specification & Planning (spec.md)

## Objective
Establish complete architectural and feature specifications before any implementation code is written. Prevent architecture drift and verify strict PS-01 alignment.

## Mandatory Steps

1. **Context Anchor**:
   - Read `project_brief.md` and `AGENTS.md` thoroughly.
   - Confirm the target tier being specified (Tiers 1 through 6).
   - Ensure out-of-scope items (voice intake, billing, external RAG) are not included.

2. **Artifact Generation**:
   - Produce a structured planning artifact before touching application source code.
   - The specification artifact must include:
     - **Feature Scope & Interfaces**: Exact function signatures, REST endpoints, and schema models.
     - **Legal Rule & Citation Compliance**: Clear demonstration of how `app/legal/deadlines.py` handles math and `{doc_id, chunk_id, page}` citation payloads.
     - **Approval & Security Gate**: Verification that all CMS write paths require `approved_by`.
     - **Test Scenarios**: Concrete unit test cases and fixtures to be evaluated.

3. **Approval Gate**:
   - Present the plan artifact for review.
   - Do NOT proceed to implementation until the plan conforms strictly to PS-01 requirements.
