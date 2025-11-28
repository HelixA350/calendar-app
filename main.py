from fastapi import FastAPI
from app.api import router
from app.database import create_tables


# Create database tables on startup
create_tables()

app = FastAPI(
    title="Calendar API",
    version="1.0.3",
    description="Простое API для получения календаря отпусков/командировок и ежедневной загрузки сотрудников.",
    root_path="/api/v1"
)

# Include API routes
app.include_router(router, prefix="/api/v1")
