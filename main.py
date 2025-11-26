from fastapi import FastAPI
from app.api import router


app = FastAPI(
    title="Work and Vacation Planning API",
    version="1.0.3",
    description="Простое API для получения календаря отпусков/командировок и ежедневной загрузки сотрудников.",
    openapi_prefix="/api/v1"
)

# Include API routes
app.include_router(router, prefix="/api/v1")
