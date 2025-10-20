from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
