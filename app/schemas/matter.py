from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MatterCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    practice_area: str = Field(..., min_length=1)
    approved_by: str = Field(..., min_length=1, description="Approving attorney identifier")


class MatterResponse(BaseModel):
    id: str
    title: str
    client_name: str
    practice_area: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
