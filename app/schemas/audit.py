from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    matter_id: Optional[str] = None
    actor: str
    action: str
    target_type: str
    target_id: str
    payload: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
