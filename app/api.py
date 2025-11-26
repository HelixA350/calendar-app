from datetime import date
from fastapi import APIRouter, HTTPException, Query

from app.models import CalendarResponseItem, WorkloadResponse
from app.services import CalendarService, WorkloadService


router = APIRouter()


@router.get("/calendar", response_model=list[CalendarResponseItem])
async def get_calendar(
    start_date: date = Query(..., description="Дата начала периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания периода (YYYY-MM-DD)")
):
    """
    Получить календарь отпусков и командировок
    """
    try:
        result = CalendarService.get_calendar(start_date, end_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workload", response_model=WorkloadResponse)
async def get_workload(
    start_date: date = Query(..., description="Дата начала периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания периода (YYYY-MM-DD)")
):
    """
    Получить ежедневную загрузку сотрудников
    """
    try:
        result = WorkloadService.get_workload(start_date, end_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))