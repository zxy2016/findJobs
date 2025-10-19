from fastapi import FastAPI
from app.db.base_class import create_all_tables
from app.db.session import engine
from app.api.v1.endpoints import scraper

app = FastAPI(
    title="FindJobs AI Assistant",
    description="An AI-powered assistant to help you find the right job.",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    create_all_tables(engine)

app.include_router(scraper.router, prefix="/api/v1", tags=["Scraper"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FindJobs AI Assistant"}

# Here we will add more routers for scraper, analysis, and matching.
