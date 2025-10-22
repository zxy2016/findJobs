from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.crud import crud_user_profile, crud_job_match
from app.schemas.job_match import JobMatch
from app.services.matching_service import MatchingService
import logging

router = APIRouter()


@router.get("/profiles/{profile_id}/recommendations", response_model=List[JobMatch])
def get_recommendations(profile_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a list of job recommendations for a user profile.
    """
    profile = crud_user_profile.get(db, id=profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    recommendations = crud_job_match.get_by_profile_id(db, profile_id=profile_id)
    return recommendations


@router.post("/profiles/{profile_id}/match", status_code=202)
def trigger_matching(
    profile_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Triggers an asynchronous job matching task for a user profile.
    """
    logging.info(f"Received request to trigger matching for profile_id: {profile_id}")
    
    profile = crud_user_profile.get(db, id=profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # 使用后台任务运行匹配服务
    matching_service = MatchingService(db)
    background_tasks.add_task(matching_service.run_matching_for_profile, profile_id)
    
    logging.info(f"Matching task for profile {profile_id} has been added to background tasks.")
    
    return {"message": "Job matching task has been triggered."}
