from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base_class import create_all_tables
from app.db.session import engine
from app.api.v1.endpoints import scraper

app = FastAPI(
    title="FindJobs AI Assistant",
    description="An AI-powered assistant to help you find the right job.",
    version="0.1.0"
)

# 配置 CORS
origins = [
    "http://localhost:3000", # 允许的前端地址
    "http://localhost",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 允许所有方法
    allow_headers=["*"], # 允许所有头部
)

@app.on_event("startup")
async def startup_event():
    # 注意：在生产环境中，数据库迁移可能需要更稳健的工具，如 Alembic
    create_all_tables(engine)

app.include_router(scraper.router, prefix="/api/v1", tags=["Scraper"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FindJobs AI Assistant"}
