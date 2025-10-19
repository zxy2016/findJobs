from app.db.session import engine
from app.db.base_class import Base
import app.models # 导入此模块以确保所有模型都被 SQLAlchemy 注册

print("Connecting to the database and creating tables...")

# 这会连接到数据库，并创建所有继承自 Base 的模型对应的表
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
