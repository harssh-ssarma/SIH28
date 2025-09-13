from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="SIH28 AI Optimization Service",
    description="AI-powered timetable optimization engine",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "SIH28 AI Optimization Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}