from sqlalchemy import Column, Integer, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    raw_content = Column(Text, nullable=False)
    structured_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
