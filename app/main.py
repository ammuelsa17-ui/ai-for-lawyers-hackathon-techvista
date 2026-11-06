import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db, init_db
from app.db.models import MatterModel, TaskModel, AuditLogModel
from app.schemas.matter import MatterCreateRequest, MatterResponse
from app.schemas.task import TaskProposeRequest, TaskApproveRequest, TaskResponse
from app.schemas.audit import AuditLogResponse
from app.cms.mock_adapter import MockCMSAdapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CasePilot Backend — PS-01 Case Management Orchestration Layer",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/matters", response_model=List[MatterResponse], tags=["Matters"])
def list_matters(db: Session = Depends(get_db)):
    return db.query(MatterModel).order_by(MatterModel.created_at.desc()).all()


@app.get("/matters/{matter_id}", response_model=MatterResponse, tags=["Matters"])
def get_matter(matter_id: str, db: Session = Depends(get_db)):
    matter = db.query(MatterModel).filter(MatterModel.id == matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


@app.post("/matters", response_model=MatterResponse, status_code=status.HTTP_201_CREATED, tags=["Matters"])
def create_matter(request: MatterCreateRequest, db: Session = Depends(get_db)):
    adapter = MockCMSAdapter(db)
    try:
        result = adapter.create_matter(
            title=request.title,
            client_name=request.client_name,
            practice_area=request.practice_area,
            approved_by=request.approved_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    matter = db.query(MatterModel).filter(MatterModel.id == result["matter_id"]).first()
    return matter


@app.get("/matters/{matter_id}/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def list_matter_tasks(
    matter_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(TaskModel).filter(TaskModel.matter_id == matter_id)
    if status_filter:
        query = query.filter(TaskModel.status == status_filter)
    return query.order_by(TaskModel.due_date.asc()).all()


@app.post("/tasks/propose", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def propose_task(request: TaskProposeRequest, db: Session = Depends(get_db)):
    """Stage a proposed task/deadline locally in CasePilot.
    
    This is local staging with status='proposed'. It does NOT execute a write
    to the external CMS adapter and sets approved_by=None.
    Manual tasks pass source_doc_id='manual' and source_chunk_id='manual'.
    """
    matter = db.query(MatterModel).filter(MatterModel.id == request.matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail=f"Matter '{request.matter_id}' not found")

    task_id = str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        matter_id=request.matter_id,
        title=request.title.strip(),
        due_date=request.due_date.strip(),
        rule_reference=request.rule_reference.strip() if request.rule_reference else None,
        status="proposed",
        source_doc_id=request.source_doc_id.strip(),
        source_chunk_id=request.source_chunk_id.strip(),
        approved_by=None,
        approved_at=None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.post("/tasks/approve", response_model=TaskResponse, tags=["Tasks"])
def approve_task(request: TaskApproveRequest, db: Session = Depends(get_db)):
    """Approve a staged proposed task and commit write-back to the CMS adapter.
    
    Requires an explicit approved_by attorney identifier. Idempotent: returns
    HTTP 409 Conflict if the task has already been approved.
    """
    task = db.query(TaskModel).filter(TaskModel.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{request.task_id}' not found")

    if task.status == "approved":
        raise HTTPException(status_code=409, detail=f"Task '{request.task_id}' is already approved by {task.approved_by}")

    adapter = MockCMSAdapter(db)
    try:
        adapter.approve_existing_task(task_id=request.task_id, approved_by=request.approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.refresh(task)
    return task


@app.get("/audit-log", response_model=List[AuditLogResponse], tags=["Audit"])
def get_audit_log(
    matter_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLogModel)
    if matter_id:
        query = query.filter(AuditLogModel.matter_id == matter_id)
    return query.order_by(AuditLogModel.created_at.desc()).all()
