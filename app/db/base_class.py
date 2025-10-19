from sqlalchemy.orm import declarative_base

# 创建所有模型都会继承的基类
Base = declarative_base()

def create_all_tables(engine):
    import app.models # 确保所有模型都被导入，以便 Base.metadata 能够发现它们
    Base.metadata.create_all(bind=engine)

