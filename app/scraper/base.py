from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Browser, Page, BrowserContext, async_playwright
from sqlalchemy.orm import Session
from app.models import Job
import asyncio

class BaseScraper(ABC):
    """
    所有招聘网站爬虫的抽象基类。
    定义了爬虫的基本结构和通用方法。
    """
    def __init__(self, db: Session):
        self.db = db
        self.site_name = self.__class__.__name__.replace("Scraper", "").lower() # 自动获取站点名称

    @abstractmethod
    async def scrape(self) -> List[Job]:
        """
        执行整个网站的爬取过程，并返回爬取到的职位列表。
        """
        pass

    async def _navigate(self, page: Page, url: str):
        pass

    async def _extract_job_links(self, page: Page) -> List[str]:
        return []

    async def _extract_job_details(self, page: Page, url: str) -> Job:
        return None

    async def _initialize_browser(self) -> Browser:
        """
        初始化并启动 Playwright 浏览器。
        """
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True) # 生产环境通常设置为 True
        return browser

    async def _close_browser(self, browser: Browser):
        """
        关闭 Playwright 浏览器。
        """
        await browser.close()

    async def _save_jobs(self, jobs: List[Job]):
        """
        将爬取到的职位列表保存到数据库。
        """
        for job in jobs:
            # 检查职位是否已存在（通过URL判断）
            existing_job = self.db.query(Job).filter(Job.url == job.url).first()
            if not existing_job:
                self.db.add(job)
        self.db.commit()
        print(f"Saved {len(jobs)} new jobs to DB from {self.site_name}.")

