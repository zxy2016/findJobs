from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Any

from app.db.session import get_db
from app.crud import crud_job
from app.schemas import job as job_schema

router = APIRouter()

@router.get("/jobs", response_model=job_schema.JobPage)
def read_jobs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="分页起始位置"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序顺序 (asc/desc)"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    location: Optional[str] = Query(None, description="按地点筛选"),
    category: Optional[str] = Query(None, description="按职能类别筛选"),
    published_days: Optional[int] = Query(None, description="按发布天数筛选 (例如: 7, 30)"),
    is_active: Optional[bool] = Query(True, description="按职位状态筛选")
) -> Any:
    """
    获取职位列表，支持分页、排序和多种筛选条件。
    """
    result = crud_job.get_multi(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
        location=location,
        category=category,
        published_days=published_days,
        is_active=is_active
    )
    return result


@router.get("/jobs/{job_id}", response_model=job_schema.Job)
def read_job(
    *, 
    db: Session = Depends(get_db), 
    job_id: int
) -> Any:
    """
    获取单个职位的详细信息。
    """
    job = crud_job.get(db, id=job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return job
