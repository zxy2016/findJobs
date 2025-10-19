from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean

from app.db.base_class import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text, nullable=False) # 职能描述，来自列表API
    url = Column(String(512), unique=True, index=True, nullable=False)
    source_site = Column(String(100), index=True, nullable=False)
    scraped_at = Column(DateTime, server_default=func.now())

    # 新增字段
    source_job_id = Column(String(100), index=True) # 来源网站的职位ID
    published_at = Column(String(100)) # 发布/更新时间
    department_info = Column(String(512)) # 部门信息 (xwinfo)
    salary_info = Column(String(255)) # 薪资标签
    experience_required = Column(String(255)) # 经验要求
    education_required = Column(String(255)) # 学历要求
    detailed_location = Column(String(512)) # 详细工作地点
    job_responsibilities = Column(Text) # 岗位职责
    job_requirements = Column(Text) # 职位要求
    contact_info = Column(String(512), nullable=True) # 联系方式
    is_active = Column(Boolean, default=True, nullable=False) # 职位是否有效

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"
