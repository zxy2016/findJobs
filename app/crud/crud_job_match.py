from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.job_match import JobMatch
from app.schemas.job_match import JobMatchCreate

def create(db: Session, *, obj_in: JobMatchCreate) -> JobMatch:
    db_obj = JobMatch(
        user_profile_id=obj_in.user_profile_id,
        job_id=obj_in.job_id,
        match_score=obj_in.match_score,
        match_summary=obj_in.match_summary
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_by_profile_id(db: Session, *, profile_id: int) -> List[JobMatch]:
    return db.query(JobMatch).options(joinedload(JobMatch.job, innerjoin=True)).filter(JobMatch.user_profile_id == profile_id).all()
