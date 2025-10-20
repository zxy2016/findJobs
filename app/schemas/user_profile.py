from pydantic import BaseModel
from typing import Dict, Any, Optional

# 创建时使用的基本模型
class UserProfileCreate(BaseModel):
    raw_content: str
    structured_profile: Dict[str, Any]
    user_id: Optional[int] = None

# 从数据库读取时使用的模型 (继承自创建模型)
class UserProfile(UserProfileCreate):
    id: int

    class Config:
        orm_mode = True
