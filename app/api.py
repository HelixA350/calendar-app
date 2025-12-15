from datetime import date
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models import *
from app.services import *
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
    

@router.delete("/events/{event_id}", response_model=DeleteEventResponse)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить событие календаря по ID
    
    Args:
        event_id: ID события для удаления
    """
    try:
        success = CalendarService.delete_event(db, CalendarEventDelete(event_id=event_id))
        if not success:
            raise HTTPException(status_code=404, detail=f"Событие с ID {event_id} не найдено")
        return DeleteEventResponse(event_id=event_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/events/{event_id}")
async def update_event_dates(
    event_id: int,
    update_data: UpdateCalendarEventDates,
    db: Session = Depends(get_db)
):
    """
    Обновить даты события календаря
    
    Args:
        event_id: ID события для обновления
        update_data: Новые даты начала и окончания
    """
    try:
        updated_event = CalendarService.update_event(
            db,
            CalendarEventUpdateDates(
                event_id=event_id,
                new_start_date=update_data.new_start_date,
                new_end_date=update_data.new_end_date,
                new_level=update_data.new_level,
        ))
        if not updated_event:
            raise HTTPException(status_code=404, detail=f"Событие с ID {event_id} не найдено")
        return UpdateEventResponse(
            event_id = updated_event.id,
            start_date = updated_event.start_date,
            end_date = updated_event.end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/departments', response_model=DepartmentsResponse)
def get_departments(db: Session = Depends(get_db)):
    data = DepartmentService.get_departments(db)
    return DepartmentsResponse(
        data
    )

@router.get('/employees', response_model=GetemployeeResponse)
def get_employees(
    department_id = Query(default=None, description='ID отдела, для которого надо получить сотрудников'),
    db: Session = Depends(get_db)
):
    data = EmployeeService.get_employees_with_departments(db, department_id)
    return data

@router.patch('/data')
def update_data(db: Session = Depends(get_db)):
    """Обновляет данные из битрикса"""
    a = BitrixService(db).sync_with_bitrix()
    return a




