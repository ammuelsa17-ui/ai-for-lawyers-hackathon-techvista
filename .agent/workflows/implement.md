# Workflow: Implementation & Verification (implement.md)

## Objective
Execute implementation following an approved specification, ensuring full test coverage and UI verification before marking any feature complete.

## Mandatory Steps

1. **Re-anchor**:
   - Confirm current task against `project_brief.md`, `AGENTS.md`, and the approved spec artifact.
   - Do not modify files outside current feature scope.

2. **Code Construction**:
   - Implement backend endpoints (FastAPI) and business logic.
   - Restrict deadline computation strictly to `app/legal/deadlines.py`.
   - Route all mock CMS writes through `app/cms/adapter.py` validating `approved_by`.
   - Enforce `{answer, citations: [{doc_id, chunk_id, page}]}` on all AI responses.

3. **Automated Testing (`pytest`)**:
   - Execute `pytest` across all existing and new unit tests.
   - Verify that test assertions pass 100% without mocks skipping `approved_by` validation.

4. **UI & End-to-End Verification**:
   - Verify Streamlit dashboard rendering and interactions.
   - Confirm that task write-back buttons trigger the approval gate correctly.
   - Confirm audit logs record the action with timestamp and approver ID.

5. **Completion Criteria**:
   - All tests passing.
   - UI inspected and verified.
   - No untracked side effects or out-of-scope code changes.
