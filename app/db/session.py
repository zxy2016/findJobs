from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import os

# 构建数据库连接字符串
# 使用 mysql+mysqldb 驱动，因为我们在 requirements.txt 中包含了 mysqlclient
SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 创建数据库引擎
# echo=True 会打印所有执行的 SQL 语句，方便调试
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # 确保连接池中的连接是活跃的
    echo=os.getenv("SQL_ECHO", "False").lower() == "true" # 根据环境变量控制是否打印SQL
)

# 创建一个 SessionLocal 类，每个 SessionLocal 实例都是一个数据库会话
# autocommit=False 意味着不会自动提交事务
# autoflush=False 意味着在查询之前不会自动刷新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
