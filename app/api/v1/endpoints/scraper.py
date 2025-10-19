from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.scraper.haier import HaierScraper
from app.task_manager import run_task_in_background, get_task_status, task_statuses
import asyncio

router = APIRouter()

# 爬虫映射字典
SCRAPERS = {
    "haier": HaierScraper,
}

# 初始化所有已知爬虫的状态为 idle
for scraper_key in SCRAPERS.keys():
    task_statuses[scraper_key] = "idle"

@router.post("/scrape/{site_name}", summary="触发指定网站的职位爬取任务")
async def trigger_scrape(
    site_name: str,
    db: Session = Depends(get_db)
):
    scraper_class = SCRAPERS.get(site_name.lower())
    if not scraper_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 '{site_name}' 对应的爬虫。"
        )
    
    # 检查任务是否已在运行
    if get_task_status(site_name) == 'running':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"任务 '{site_name}' 已在运行中，请勿重复触发。"
        )

    scraper_instance = scraper_class(db=db)
    # 使用新的任务管理器在后台运行爬虫
    asyncio.create_task(run_task_in_background(site_name, scraper_instance.scrape))

    return {"message": f"已成功提交 '{site_name}' 爬虫任务。"}

@router.get("/scrape/status/{site_name}", summary="获取指定爬虫任务的状态")
async def get_scrape_status(site_name: str):
    if site_name.lower() not in SCRAPERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 '{site_name}' 对应的爬虫。"
        )
    
    status = get_task_status(site_name.lower())
    return {"site_name": site_name, "status": status}