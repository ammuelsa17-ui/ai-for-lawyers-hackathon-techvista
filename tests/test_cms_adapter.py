import pytest
from app.cms.mock_adapter import MockCMSAdapter
from app.db.models import MatterModel, TaskModel, DocumentModel, AuditLogModel


def test_adapter_requires_approval(db_session):
    """Assert all 4 CMS adapter methods reject empty, whitespace, or None approved_by."""
    adapter = MockCMSAdapter(db_session)

    # 1. create_matter
    for bad_approval in ("", "   ", None):
        with pytest.raises(ValueError, match="approved_by is required"):
            adapter.create_matter("Matter Title", "Client X", "Litigation", approved_by=bad_approval)

    # Create a valid matter for subsequent tests
    matter_result = adapter.create_matter("Matter Title", "Client X", "Litigation", approved_by="attorney_jane")
    matter_id = matter_result["matter_id"]

    # 2. create_task
    for bad_approval in ("", "   ", None):
        with pytest.raises(ValueError, match="approved_by is required"):
            adapter.create_task(matter_id, "Task Title", "2026-12-01", None, "doc1", "chunk1", approved_by=bad_approval)

    # 3. add_note
    for bad_approval in ("", "   ", None):
        with pytest.raises(ValueError, match="approved_by is required"):
            adapter.add_note(matter_id, "Case note text", approved_by=bad_approval)

    # Seed a document for tag_document test
    doc = DocumentModel(
        id="doc_test_1",
        matter_id=matter_id,
        file_name="pleading.txt",
        file_path="fixtures/pleading.txt",
        category="Unclassified",
        page_count=2,
    )
    db_session.add(doc)
    db_session.commit()

    # 4. tag_document
    for bad_approval in ("", "   ", None):
        with pytest.raises(ValueError, match="approved_by is required"):
            adapter.tag_document("doc_test_1", matter_id, "Pleading", approved_by=bad_approval)


def test_create_task_requires_citations(db_session):
    """Assert create_task strictly requires non-empty source_doc_id and source_chunk_id."""
    adapter = MockCMSAdapter(db_session)
    matter_result = adapter.create_matter("Matter Title", "Client X", "Litigation", approved_by="attorney_jane")
    matter_id = matter_result["matter_id"]

    # Empty source_doc_id
    with pytest.raises(ValueError, match="source_doc_id is required"):
        adapter.create_task(matter_id, "Task Title", "2026-12-01", None, "", "chunk1", approved_by="attorney_jane")

    # Empty source_chunk_id
    with pytest.raises(ValueError, match="source_chunk_id is required"):
        adapter.create_task(matter_id, "Task Title", "2026-12-01", None, "doc1", "   ", approved_by="attorney_jane")

    # Valid call succeeds and persists citations
    task_res = adapter.create_task(
        matter_id, "File Answer", "2026-12-01", "FRCP Rule 12", "doc_summons", "chunk_par_4", approved_by="attorney_jane"
    )
    task_id = task_res["task_id"]
    task = db_session.query(TaskModel).filter(TaskModel.id == task_id).first()
    assert task is not None
    assert task.source_doc_id == "doc_summons"
    assert task.source_chunk_id == "chunk_par_4"
    assert task.approved_by == "attorney_jane"
    assert task.status == "approved"


def test_all_adapter_calls_produce_audit_log(db_session):
    """Assert every single adapter call records an immutable row in audit_log with actor and matter_id."""
    adapter = MockCMSAdapter(db_session)

    # 1. create_matter
    m_res = adapter.create_matter("Acme Matter", "Acme", "Labor", approved_by="attorney_a")
    matter_id = m_res["matter_id"]

    # 2. create_task
    adapter.create_task(matter_id, "File Motion", "2026-11-20", None, "manual", "manual", approved_by="attorney_b")

    # 3. add_note
    adapter.add_note(matter_id, "Settlement offer received", approved_by="attorney_c")

    # 4. tag_document
    doc = DocumentModel(
        id="d1",
        matter_id=matter_id,
        file_name="motion.pdf",
        file_path="data/motion.pdf",
        category="Unclassified",
    )
    db_session.add(doc)
    db_session.commit()
    adapter.tag_document("d1", matter_id, "Motion", approved_by="attorney_d")

    # Verify audit_log table has 4 distinct entries
    audit_rows = db_session.query(AuditLogModel).order_by(AuditLogModel.created_at.asc()).all()
    assert len(audit_rows) == 4

    actions = [r.action for r in audit_rows]
    actors = [r.actor for r in audit_rows]
    assert actions == ["create_matter", "create_task", "add_note", "tag_document"]
    assert actors == ["attorney_a", "attorney_b", "attorney_c", "attorney_d"]
    for r in audit_rows:
        assert r.matter_id == matter_id


def test_two_stage_approval_flow_and_idempotency(client):
    """Assert staging a proposed task is local-only, approval commits to CMS and audit log, and is idempotent."""
    # 1. Create a matter via API
    m_resp = client.post(
        "/matters",
        json={"title": "Contract Dispute", "client_name": "Initech", "practice_area": "Litigation", "approved_by": "attorney_init"},
    )
    assert m_resp.status_code == 201
    matter_id = m_resp.json()["id"]

    # Check audit log contains create_matter
    audit_resp = client.get("/audit-log")
    assert len(audit_resp.json()) == 1

    # 2. Stage a proposed task (AI extraction simulation)
    propose_resp = client.post(
        "/tasks/propose",
        json={
            "matter_id": matter_id,
            "title": "Respond to Interrogatories",
            "due_date": "2026-12-15",
            "rule_reference": "FRCP 33",
            "source_doc_id": "doc_discovery_req",
            "source_chunk_id": "chunk_004",
        },
    )
    assert propose_resp.status_code == 201
    task_data = propose_resp.json()
    assert task_data["status"] == "proposed"
    assert task_data["approved_by"] is None
    assert task_data["approved_at"] is None
    task_id = task_data["id"]

    # CRITICAL: Verify NO audit log entry was created for proposed task staging
    audit_resp2 = client.get("/audit-log")
    assert len(audit_resp2.json()) == 1  # Still just create_matter

    # 3. Approve task via approval gate
    approve_resp = client.post(
        "/tasks/approve",
        json={"task_id": task_id, "approved_by": "attorney_reviewer"},
    )
    assert approve_resp.status_code == 200
    approved_task = approve_resp.json()
    assert approved_task["status"] == "approved"
    assert approved_task["approved_by"] == "attorney_reviewer"
    assert approved_task["approved_at"] is not None

    # Verify audit log now records the approved task write
    audit_resp3 = client.get("/audit-log")
    assert len(audit_resp3.json()) == 2
    task_audit = audit_resp3.json()[0]  # Most recent
    assert task_audit["action"] == "create_task"
    assert task_audit["actor"] == "attorney_reviewer"
    assert task_audit["matter_id"] == matter_id

    # 4. Idempotency test: Double approval returns 409 Conflict
    dup_approve = client.post(
        "/tasks/approve",
        json={"task_id": task_id, "approved_by": "attorney_reviewer"},
    )
    assert dup_approve.status_code == 409


def test_health_and_matter_detail_endpoints(client):
    """Verify health check and single matter detail endpoints."""
    # Health check
    h_resp = client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "ok"
    assert h_resp.json()["app"] == "CasePilot"

    # Create matter
    m_resp = client.post(
        "/matters",
        json={"title": "Single Matter Test", "client_name": "Test Client", "practice_area": "IP", "approved_by": "attorney_ip"},
    )
    m_id = m_resp.json()["id"]

    # Get single matter
    get_resp = client.get(f"/matters/{m_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Single Matter Test"

    # Non-existent matter 404
    bad_resp = client.get("/matters/non_existent_id")
    assert bad_resp.status_code == 404
