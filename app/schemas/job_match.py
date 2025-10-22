from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from .job import Job

# Shared properties
class JobMatchBase(BaseModel):
    user_profile_id: int
    job_id: int
    match_score: float
    match_summary: str
    improvement_suggestions: Optional[str] = None

# Properties to receive on item creation
class JobMatchCreate(JobMatchBase):
    pass

# Properties to receive on item update
class JobMatchUpdate(JobMatchBase):
    pass

# Properties shared by models stored in DB
class JobMatchInDBBase(JobMatchBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class JobMatch(JobMatchInDBBase):
    job: Job  # 明确包含 job 对象

# Properties stored in DB
class JobMatchInDB(JobMatchInDBBase):
    pass
