from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class MatterModel(Base):
    __tablename__ = "matters"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    practice_area = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    tasks = relationship("TaskModel", back_populates="matter", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="matter", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    matter_id = Column(String, ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    due_date = Column(String, nullable=False)
    rule_reference = Column(String, nullable=True)
    status = Column(String, nullable=False, default="proposed")
    source_doc_id = Column(String, nullable=False)
    source_chunk_id = Column(String, nullable=False)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    matter = relationship("MatterModel", back_populates="tasks")


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    matter_id = Column(String, ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    category = Column(String, default="Unclassified")
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    matter = relationship("MatterModel", back_populates="documents")


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)
    matter_id = Column(String, nullable=True)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
