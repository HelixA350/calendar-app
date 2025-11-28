from datetime import date
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models import CalendarResponseItem, WorkloadResponse, CreateCalendarEvent, CreateCalendarEventResponse
from app.services import CalendarService, WorkloadService
from app.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/calendar", response_model=list[CalendarResponseItem])
async def get_calendar(
    start_date: date = Query(..., description="Дата начала периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания периода (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Получить календарь отпусков и командировок
    """
    try:
        result = CalendarService.get_calendar(db, start_date, end_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workload", response_model=WorkloadResponse)
async def get_workload(
    start_date: date = Query(..., description="Дата начала периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания периода (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Получить ежедневную загрузку сотрудников
    """
    try:
        result = WorkloadService.get_workload(db, start_date, end_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/events", response_model=CreateCalendarEventResponse)
async def create_event(
    event_data: CreateCalendarEvent,
    db: Session = Depends(get_db)
):
    """
    Создать новое событие (отпуск или командировка)
    """
    try:
        result = CalendarService.create_event(db, event_data)
        return CreateCalendarEventResponse(id=result.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))