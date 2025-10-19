from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.scraper.haier import HaierScraper # 暂时注释掉，等 HaierScraper 实现

router = APIRouter()

# 爬虫映射字典，未来可以动态加载
SCRAPERS = {
    "haier": HaierScraper,
}

@router.post("/scrape/{site_name}", summary="触发指定网站的职位爬取任务")
async def trigger_scrape(
    site_name: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    触发指定招聘网站的职位爬取任务。
    爬取任务将在后台运行，API会立即返回。
    """
    scraper_class = SCRAPERS.get(site_name.lower())
    if not scraper_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 '{site_name}' 对应的爬虫。"
        )

    scraper_instance = scraper_class(db=db)
    background_tasks.add_task(scraper_instance.scrape)

    return {"message": f"已成功在后台启动 '{site_name}' 爬虫任务。"}
