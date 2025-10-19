from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# API 响应中单个 Job 的模型
class Job(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: str
    source_site: str
    department_info: Optional[str] = None # 部门信息
    published_at: Optional[str] = None
    salary_info: Optional[str] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    detailed_location: Optional[str] = None
    job_responsibilities: Optional[str] = None
    job_requirements: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True # 允许从 ORM 对象（SQLAlchemy 模型）转换

# API 响应的整体模型，包含分页信息和动态筛选选项
class JobPage(BaseModel):
    total: int
    items: List[Job]
    available_locations: List[str]
    available_categories: List[str]
