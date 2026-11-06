import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.cms.adapter import CMSAdapter
from app.db.models import MatterModel, TaskModel, DocumentModel, AuditLogModel


class MockCMSAdapter(CMSAdapter):
    """Concrete mock adapter simulating a legal Case Management System.
    
    Persists updates to local SQLite storage and records an immutable
    audit log entry for every executed operation.
    """

    def __init__(self, db: Session):
        self.db = db

    def _record_audit(
        self,
        actor: str,
        action: str,
        target_type: str,
        target_id: str,
        payload: Dict[str, Any],
        matter_id: Optional[str] = None,
    ) -> AuditLogModel:
        audit_entry = AuditLogModel(
            id=str(uuid.uuid4()),
            matter_id=matter_id,
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=json.dumps(payload),
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(audit_entry)
        self.db.flush()
        return audit_entry

    def create_matter(
        self,
        title: str,
        client_name: str,
        practice_area: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        approver = self.validate_approval(approved_by)
        matter_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        matter = MatterModel(
            id=matter_id,
            title=title.strip(),
            client_name=client_name.strip(),
            practice_area=practice_area.strip(),
            status="open",
            created_at=now,
            updated_at=now,
        )
        self.db.add(matter)
        self.db.flush()

        self._record_audit(
            actor=approver,
            action="create_matter",
            target_type="matter",
            target_id=matter_id,
            payload={"title": title, "client_name": client_name, "practice_area": practice_area},
            matter_id=matter_id,
        )
        self.db.commit()
        return {
            "status": "committed",
            "matter_id": matter_id,
            "title": title,
            "approved_by": approver,
        }

    def create_task(
        self,
        matter_id: str,
        title: str,
        due_date: str,
        rule_reference: Optional[str],
        source_doc_id: str,
        source_chunk_id: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        approver = self.validate_approval(approved_by)
        doc_id, chunk_id = self.validate_citations(source_doc_id, source_chunk_id)

        # Verify matter exists to uphold relational integrity
        matter = self.db.query(MatterModel).filter(MatterModel.id == matter_id).first()
        if not matter:
            raise ValueError(f"Matter with id '{matter_id}' does not exist.")

        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        task = TaskModel(
            id=task_id,
            matter_id=matter_id,
            title=title.strip(),
            due_date=due_date.strip(),
            rule_reference=rule_reference.strip() if rule_reference else None,
            status="approved",
            source_doc_id=doc_id,
            source_chunk_id=chunk_id,
            approved_by=approver,
            approved_at=now,
            created_at=now,
        )
        self.db.add(task)
        self.db.flush()

        self._record_audit(
            actor=approver,
            action="create_task",
            target_type="task",
            target_id=task_id,
            payload={
                "title": title,
                "due_date": due_date,
                "rule_reference": rule_reference,
                "source_doc_id": doc_id,
                "source_chunk_id": chunk_id,
            },
            matter_id=matter_id,
        )
        self.db.commit()
        return {
            "status": "committed",
            "task_id": task_id,
            "matter_id": matter_id,
            "title": title,
            "approved_by": approver,
            "approved_at": now.isoformat(),
        }

    def approve_existing_task(
        self,
        task_id: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Approve an already staged (status='proposed') task and commit it to CMS."""
        approver = self.validate_approval(approved_by)
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task with id '{task_id}' not found.")
        if task.status == "approved":
            return {
                "status": "already_approved",
                "task_id": task_id,
                "approved_by": task.approved_by,
            }

        now = datetime.now(timezone.utc)
        task.status = "approved"
        task.approved_by = approver
        task.approved_at = now

        self._record_audit(
            actor=approver,
            action="create_task",
            target_type="task",
            target_id=task.id,
            payload={
                "title": task.title,
                "due_date": task.due_date,
                "rule_reference": task.rule_reference,
                "source_doc_id": task.source_doc_id,
                "source_chunk_id": task.source_chunk_id,
            },
            matter_id=task.matter_id,
        )
        self.db.commit()
        return {
            "status": "committed",
            "task_id": task.id,
            "matter_id": task.matter_id,
            "approved_by": approver,
            "approved_at": now.isoformat(),
        }

    def add_note(
        self,
        matter_id: str,
        content: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        approver = self.validate_approval(approved_by)
        matter = self.db.query(MatterModel).filter(MatterModel.id == matter_id).first()
        if not matter:
            raise ValueError(f"Matter with id '{matter_id}' does not exist.")

        note_id = str(uuid.uuid4())
        self._record_audit(
            actor=approver,
            action="add_note",
            target_type="note",
            target_id=note_id,
            payload={"content": content},
            matter_id=matter_id,
        )
        self.db.commit()
        return {
            "status": "committed",
            "note_id": note_id,
            "matter_id": matter_id,
            "approved_by": approver,
        }

    def tag_document(
        self,
        document_id: str,
        matter_id: str,
        tag: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        approver = self.validate_approval(approved_by)
        document = self.db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not document:
            raise ValueError(f"Document with id '{document_id}' not found.")

        document.category = tag.strip()
        self._record_audit(
            actor=approver,
            action="tag_document",
            target_type="document",
            target_id=document_id,
            payload={"tag": tag},
            matter_id=matter_id,
        )
        self.db.commit()
        return {
            "status": "committed",
            "document_id": document_id,
            "tag": tag,
            "approved_by": approver,
        }
