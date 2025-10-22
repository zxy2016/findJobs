from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate # This schema doesn't exist yet, I'll create it.

def get(db: Session, id: Any) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.id == id).first()

def create_user_profile(db: Session, *, obj_in: UserProfileCreate) -> UserProfile:
    """
    创建一个新的用户画像条目。
    """
    db_obj = UserProfile(
        # user_id=obj_in.user_id, # We might not have a user context yet
        raw_content=obj_in.raw_content,
        structured_profile=obj_in.structured_profile
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
