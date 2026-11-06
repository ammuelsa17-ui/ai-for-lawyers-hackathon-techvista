from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskProposeRequest(BaseModel):
    matter_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    due_date: str = Field(..., min_length=1, pattern=r"^\d{4}-\d{2}-\d{2}$")
    rule_reference: Optional[str] = None
    source_doc_id: str = Field(default="manual", min_length=1)
    source_chunk_id: str = Field(default="manual", min_length=1)


class TaskApproveRequest(BaseModel):
    task_id: str = Field(..., min_length=1)
    approved_by: str = Field(..., min_length=1, description="Approving attorney identifier")


class TaskResponse(BaseModel):
    id: str
    matter_id: str
    title: str
    due_date: str
    rule_reference: Optional[str] = None
    status: str
    source_doc_id: str
    source_chunk_id: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
