from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from app.models.job import Job
from typing import Optional

def get(db: Session, *, id: int) -> Optional[Job]:
    """
    根据 ID 获取单个职位。
    """
    return db.query(Job).filter(Job.id == id).first()

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
    为每个筛选器动态生成其独立的可用选项列表。
    """
    
    # --- 基础查询构建函数 ---
    def build_base_query(exclude_filter: Optional[str] = None):
        query = db.query(Job)
        if is_active is not None:
            query = query.filter(Job.is_active == is_active)
        
        if location and exclude_filter != 'location':
            query = query.filter(Job.location == location)
        
        if category and exclude_filter != 'category':
            query = query.filter(Job.description == category)

        if published_days:
            from datetime import datetime, timedelta
            since_date = datetime.utcnow() - timedelta(days=published_days)
            query = query.filter(Job.published_at >= str(since_date.date()))

        if keyword:
            search_keyword = f"%{keyword}%"
            query = query.filter(
                (
                    Job.title.ilike(search_keyword) |
                    Job.description.ilike(search_keyword) |
                    Job.job_responsibilities.ilike(search_keyword) |
                    Job.job_requirements.ilike(search_keyword) |
                    Job.department_info.ilike(search_keyword)
                )
            )
        return query

    # --- 1. 获取动态筛选选项 ---

    # 获取可用的地点 (排除地点自身筛选)
    locations_query = build_base_query(exclude_filter='location')
    available_locations_result = locations_query.with_entities(Job.location).distinct().all()
    available_locations = [loc[0] for loc in available_locations_result if loc[0]]

    # 获取可用的职能类别 (排除职能类别自身筛选)
    categories_query = build_base_query(exclude_filter='category')
    available_categories_result = categories_query.with_entities(Job.description).distinct().all()
    available_categories = [cat[0] for cat in available_categories_result if cat[0]]

    # --- 2. 获取最终的职位列表 ---
    
    # 应用所有筛选条件
    final_query = build_base_query()
    
    total = final_query.count()

    # 排序逻辑
    if sort_by and hasattr(Job, sort_by):
        order_column = getattr(Job, sort_by)
        if sort_order == 'asc':
            final_query = final_query.order_by(asc(order_column))
        else:
            final_query = final_query.order_by(desc(order_column))
    else:
        # 默认按发布/更新时间排序
        final_query = final_query.order_by(desc(Job.published_at))

    # 分页逻辑
    jobs = final_query.offset(skip).limit(limit).all()

    return {
        "total": total, 
        "items": jobs,
        "available_locations": available_locations,
        "available_categories": available_categories
    }
