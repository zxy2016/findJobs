import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Job
from app.db.base_class import Base
from app.db.session import SQLALCHEMY_DATABASE_URL
from app.scraper.haier import HaierScraper

# 使用一个独立的测试数据库URL
# 注意：这里假设您的MySQL服务器上可以创建并访问 find_jobs_test_scraper 数据库
TEST_SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("find_jobs", "find_jobs_test_scraper")

# 创建测试数据库引擎
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

# 创建测试会话
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def db_session_for_scraper():
    # 在测试模块开始前创建所有表
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 在测试模块结束后删除所有表
        Base.metadata.drop_all(bind=test_engine)

@pytest.mark.asyncio
async def test_haier_scraper_integration(db_session_for_scraper: Session):
    # 清空数据库，确保每次测试都是干净的
    db_session_for_scraper.query(Job).delete()
    db_session_for_scraper.commit()

    scraper = HaierScraper(db=db_session_for_scraper)
    scraped_jobs = await scraper.scrape()

    # 验证爬取到的职位数量
    assert len(scraped_jobs) > 0, "HaierScraper should have scraped some jobs."

    # 验证数据库中是否有数据
    jobs_in_db = db_session_for_scraper.query(Job).filter(Job.source_site == "haier").all()
    assert len(jobs_in_db) >= len(scraped_jobs), "Scraped jobs should be in the database."

    # 验证数据的基本完整性
    for job in jobs_in_db:
        assert job.title is not None and job.title != ""
        assert job.url is not None and job.url != ""
        assert job.description is not None and job.description != ""
        assert job.source_site == "haier"
        assert "海尔集团" in job.company # 验证公司名称是否正确

    print(f"Successfully scraped and verified {len(jobs_in_db)} jobs from Haier.")
