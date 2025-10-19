from typing import List, Dict, Any
from playwright.async_api import Page, Browser
from sqlalchemy.orm import Session
from app.models import Job
from app.scraper.base import BaseScraper
import asyncio
import random
import re
import json

class HaierScraper(BaseScraper):
    BASE_URL = "https://maker.haier.net/client/job/index"

    def __init__(self, db: Session):
        super().__init__(db)
        self.site_name = "haier"

    async def scrape(self) -> List[Job]:
        print("Starting incremental scrape for Haier...")
        browser = await self._initialize_browser()
        
        online_jobs_map = await self._get_online_snapshot(browser)
        if not online_jobs_map:
            print("Could not fetch online job list. Aborting.")
            await self._close_browser(browser)
            return []

        print("Comparing online snapshot with database...")
        db_jobs_map = {job.source_job_id: job for job in self.db.query(Job).filter(Job.source_site == self.site_name).all()}
        
        new_job_ids, updated_job_ids = [], []
        online_job_ids, db_job_ids = set(online_jobs_map.keys()), set(db_jobs_map.keys())

        for job_id, online_job_data in online_jobs_map.items():
            if job_id not in db_job_ids:
                new_job_ids.append(job_id)
            else:
                db_job = db_jobs_map[job_id]
                if online_job_data.get('update_time') > db_job.published_at:
                    updated_job_ids.append(job_id)
        
        jobs_to_deactivate_ids = db_job_ids - online_job_ids

        print(f"Found {len(new_job_ids)} new jobs, {len(updated_job_ids)} updated jobs, and {len(jobs_to_deactivate_ids)} jobs to deactivate.")

        jobs_to_process_ids = new_job_ids + updated_job_ids
        if jobs_to_process_ids:
            print(f"Scraping details for {len(jobs_to_process_ids)} jobs...")
            for i, job_id in enumerate(jobs_to_process_ids):
                job_item = online_jobs_map[job_id]
                print(f"Processing job {i+1}/{len(jobs_to_process_ids)}: {job_item.get('job_name')}")
                details = await self._scrape_job_details(browser, job_id)
                self._upsert_job(job_item, details)
                await asyncio.sleep(random.uniform(0.5, 1.5))

        if jobs_to_deactivate_ids:
            print(f"Deactivating {len(jobs_to_deactivate_ids)} jobs...")
            self.db.query(Job).filter(Job.source_job_id.in_(jobs_to_deactivate_ids)).update({'is_active': False}, synchronize_session=False)

        self.db.commit()
        print("Incremental scrape finished and database is updated.")
        await self._close_browser(browser)
        return []

    async def _get_online_snapshot(self, browser: Browser) -> Dict[str, Dict]:
        print("Fetching online job snapshot using page.evaluate(fetch)...")
        snapshot_map = {}
        page = await browser.new_page()
        total_jobs = 0

        try:
            await page.goto(self.BASE_URL, wait_until="networkidle")

            api_url_page1 = "https://maker.haier.net/client/job/searchdata.html?page=1&pagesize=10"
            json_data = await page.evaluate(f"fetch('{api_url_page1}').then(response => response.json())")
            
            if json_data.get("data"):
                total_jobs = json_data["data"].get("count", 0)
                if json_data["data"].get("list"):
                    for item in json_data["data"]["list"]:
                        snapshot_map[item['id']] = item

            if total_jobs > 0:
                total_pages = (total_jobs + 9) // 10
                print(f"Snapshot: Total jobs={total_jobs}, Total pages={total_pages}")
                for i in range(2, total_pages + 1):
                    api_url = f"https://maker.haier.net/client/job/searchdata.html?page={i}&pagesize=10"
                    page_data = await page.evaluate(f"fetch('{api_url}').then(response => response.json())")
                    if page_data.get("data") and page_data["data"].get("list"):
                        for item in page_data["data"]["list"]:
                            snapshot_map[item['id']] = item
        except Exception as e:
            print(f"Error fetching online snapshot: {e}")
        finally:
            await page.close()
        
        print(f"Snapshot created with {len(snapshot_map)} jobs.")
        return snapshot_map

    def _upsert_job(self, item: Dict, details: Dict):
        job_id = item.get("id")
        existing_job = self.db.query(Job).filter(Job.source_job_id == job_id).first()

        if existing_job:
            existing_job.title = item.get("job_name")
            existing_job.location = item.get("location")
            existing_job.description = item.get("func_desc")
            existing_job.published_at = item.get("update_time")
            existing_job.department_info = item.get("xwinfo")
            existing_job.salary_info = item.get("salary_label")
            existing_job.experience_required = item.get("work_experience_label")
            existing_job.education_required = item.get("education_required_label")
            existing_job.job_responsibilities = details.get("job_responsibilities")
            existing_job.job_requirements = details.get("job_requirements")
            existing_job.detailed_location = details.get("detailed_location")
            existing_job.contact_info = details.get("contact_info")
            existing_job.is_active = True
        else:
            new_job = Job(
                title=item.get("job_name"),
                company="海尔集团",
                location=item.get("location"),
                description=item.get("func_desc"),
                url=f"https://maker.haier.net/client/job/detail?id={job_id}",
                source_site=self.site_name,
                source_job_id=job_id,
                published_at=item.get("update_time"),
                department_info=item.get("xwinfo"),
                salary_info=item.get("salary_label"),
                experience_required=item.get("work_experience_label"),
                education_required=item.get("education_required_label"),
                job_responsibilities=details.get("job_responsibilities"),
                job_requirements=details.get("job_requirements"),
                detailed_location=details.get("detailed_location"),
                contact_info=details.get("contact_info"),
                is_active=True
            )
            self.db.add(new_job)

    async def _scrape_job_details(self, browser: Browser, job_id: str) -> Dict[str, str]:
        details = {}
        context = None
        page = None
        url = f"https://maker.haier.net/client/job/detail?id={job_id}"
        try:
            context = await browser.new_context(java_script_enabled=True)
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)

            details["job_responsibilities"] = (await page.locator("//div[span[contains(text(), '职责描述')]]/following-sibling::div[1]").text_content(timeout=5000)).strip()
            details["job_requirements"] = (await page.locator("//div[span[contains(text(), '任职要求')]]/following-sibling::div[1]").text_content(timeout=5000)).strip()
            details["detailed_location"] = (await page.locator("//div[span[contains(text(), '工作地点')]]/following-sibling::div[1]").text_content(timeout=5000)).strip()
            
            try:
                contact_email_raw = await page.locator("//p[i[contains(@class, 'icon-user-line')]]").text_content(timeout=100)
                if contact_email_raw:
                    details["contact_info"] = re.sub(r'\s+', ' ', contact_email_raw).strip()
            except Exception:
                details["contact_info"] = None

        except Exception as e:
            print(f"Could not scrape details from {url}: {e}")
        finally:
            if page: await page.close()
            if context: await context.close()
        return details
