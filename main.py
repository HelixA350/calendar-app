from fastapi import FastAPI
from app.api import router
from app.database import create_tables
from fastapi.middleware.cors import CORSMiddleware


# Create database tables on startup
create_tables()

app = FastAPI(
    title="Calendar API",
    version="1.0.3",
    description="Простое API для получения календаря отпусков/командировок и ежедневной загрузки сотрудников.",
)

# Include API routes
app.include_router(router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
