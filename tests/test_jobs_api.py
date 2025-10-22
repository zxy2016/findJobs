import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models import Job
from app.db.base_class import Base

# 使用独立的测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_jobs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 重写 get_db 依赖，以使用测试数据库
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 使用 TestClient
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # 创建表
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 填充模拟数据
    jobs_data = [
        Job(title="Python Developer", location="青岛", description="python dev", url="url1", source_site="test", published_at="2025-10-20", is_active=True),
        Job(title="Frontend Developer", location="北京", description="react dev", url="url2", source_site="test", published_at="2025-10-21", is_active=True),
        Job(title="Data Scientist", location="北京", description="data analysis", url="url3", source_site="test", published_at="2025-10-22", is_active=True),
        Job(title="Backend Developer (Java)", location="青岛", description="java dev", url="url4", source_site="test", published_at="2025-10-19", is_active=False),
    ]
    db.add_all(jobs_data)
    db.commit()

    yield

    # 清理
    Base.metadata.drop_all(bind=engine)


def test_read_jobs_default(setup_database):
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3 # 默认 is_active=True
    assert len(data["items"]) == 3
    # 默认按 published_at 降序
    assert data["items"][0]["title"] == "Data Scientist"


def test_read_jobs_pagination(setup_database):
    response = client.get("/api/v1/jobs?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Frontend Developer"


def test_read_jobs_sorting(setup_database):
    response = client.get("/api/v1/jobs?sort_by=title&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["title"] == "Data Scientist"


def test_read_jobs_filter_by_location(setup_database):
    response = client.get("/api/v1/jobs?location=青岛")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Developer"


def test_read_jobs_filter_by_keyword(setup_database):
    response = client.get("/api/v1/jobs?keyword=dev")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2 # Python Dev 和 Frontend Dev


def test_read_jobs_filter_by_is_active(setup_database):
    response = client.get("/api/v1/jobs?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Backend Developer (Java)"

def test_read_single_job(setup_database):
    # 测试获取存在的职位
    response = client.get("/api/v1/jobs/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python Developer"
    assert data["id"] == 1

    # 测试获取不存在的职位
    response = client.get("/api/v1/jobs/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

