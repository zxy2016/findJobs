from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.job import Job

router = APIRouter()

@router.get("/jobs/locations", response_model=List[str], summary="获取所有不重复的工作地点")
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Job.location).distinct().all()
    return [loc[0] for loc in locations if loc[0]]

@router.get("/jobs/categories", response_model=List[str], summary="获取所有不重复的职能类别")
def get_categories(db: Session = Depends(get_db)):
    # 使用 description 字段作为职能类别
    categories = db.query(Job.description).distinct().all()
    return [cat[0] for cat in categories if cat[0]]
