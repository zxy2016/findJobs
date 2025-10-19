import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Job
from app.db.base_class import Base
from app.db.session import SQLALCHEMY_DATABASE_URL # 使用已定义的URL

# 使用一个独立的测试数据库URL，或者确保测试数据库是空的
# 注意：这里假设您的MySQL服务器上可以创建并访问 find_jobs_test 数据库
TEST_SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("find_jobs", "find_jobs_test")

# 创建测试数据库引擎
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

# 创建测试会话
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def db_session():
    # 在测试模块开始前创建所有表
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 在测试模块结束后删除所有表
        Base.metadata.drop_all(bind=test_engine)

def test_create_job(db_session: Session):
    job_data = {
        "title": "软件工程师",
        "company": "测试公司",
        "location": "北京",
        "description": "负责软件开发和维护。",
        "url": "http://test.com/job/1",
        "source_site": "test_site"
    }
    new_job = Job(**job_data)
    db_session.add(new_job)
    db_session.commit()
    db_session.refresh(new_job)

    assert new_job.id is not None
    assert new_job.title == job_data["title"]
    assert new_job.company == job_data["company"]
    assert new_job.location == job_data["location"]
    assert new_job.description == job_data["description"]
    assert new_job.url == job_data["url"]
    assert new_job.source_site == job_data["source_site"]
    assert new_job.scraped_at is not None

    # 验证唯一性约束
    # 尝试添加一个URL相同的职位，应该会引发IntegrityError
    with pytest.raises(Exception) as excinfo:
        duplicate_job = Job(**job_data)
        db_session.add(duplicate_job)
        db_session.commit()
    assert "Duplicate entry" in str(excinfo.value) or "UNIQUE constraint failed" in str(excinfo.value)
