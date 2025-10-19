from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.job import Job
from typing import Optional

def get_multi(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = 'desc',
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None, # 新增：职能类别
    published_days: Optional[int] = None, # 新增：发布天数
    is_active: Optional[bool] = None
):
    """
    获取职位列表，支持分页、排序和筛选。
    """
    query = db.query(Job)

    # 筛选逻辑
    if is_active is not None:
        query = query.filter(Job.is_active == is_active)
    
    if location:
        query = query.filter(Job.location == location) # 精确匹配
    
    if category:
        query = query.filter(Job.description == category) # 精确匹配

    if published_days:
        from datetime import datetime, timedelta
        since_date = datetime.utcnow() - timedelta(days=published_days)
        # 假设 published_at 是字符串，需要转换
        query = query.filter(Job.published_at >= str(since_date.date()))

    if keyword:
        # 支持对多个字段进行模糊搜索
        search_keyword = f"%{keyword}%"
        query = query.filter(
            (
                Job.title.ilike(search_keyword) |
                Job.description.ilike(search_keyword) |
                Job.job_responsibilities.ilike(search_keyword) |
                Job.job_requirements.ilike(search_keyword) |
                Job.department_info.ilike(search_keyword) # 新增部门信息搜索
            )
        )

    total = query.count()

    # 排序逻辑
    if sort_by and hasattr(Job, sort_by):
        order_column = getattr(Job, sort_by)
        if sort_order == 'asc':
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
    else:
        # 默认按发布/更新时间排序
        query = query.order_by(desc(Job.published_at))

    # 分页逻辑
    jobs = query.offset(skip).limit(limit).all()

    return {"total": total, "items": jobs}
