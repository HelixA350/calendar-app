from datetime import date
from typing import List
from pydantic import BaseModel
from typing import Literal, Optional

class EmployeeInfo(BaseModel):
    id: int
    full_name: str

class CreateEmployee(BaseModel):
    full_name: str

class CreateEmployeeResponse(BaseModel):
    id: int


class CalendarEvent(BaseModel):
    type: Literal['vacation', 'business_trip']  # "vacation" or "business_trip"
    start: date
    end: date

class CalendarEventDelete(BaseModel):
    event_id: int

class UpdateCalendarEventDates(BaseModel):
    new_start_date: Optional[date] = None
    new_end_date: Optional[date] = None

class CalendarEventUpdateDates(BaseModel):
    event_id: int
    new_start_date: Optional[date] = None
    new_end_date: Optional[date] = None

class UpdateEventResponse(BaseModel):
    event_id: int
    status: str = 'Даты успешно обновлены'
    start_date: date
    end_date: date

class DailyWorkload(BaseModel):
    date: date
    percent: float

class CreateCalendarEvent(BaseModel):
    employee_id: int
    type: Literal['vacation', 'business_trip']  # "vacation" or "business_trip"
    start: date
    end: date

class CreateCalendarEventResponse(BaseModel):
    id: int


# Response models
class CalendarResponseItem(BaseModel):
    employee: EmployeeInfo
    events: List[CalendarEvent]


class WorkloadResponseItem(BaseModel):
    employee: EmployeeInfo
    workload: List[DailyWorkload]


class WorkloadResponse(BaseModel):
    employees: List[WorkloadResponseItem]
    total: List[DailyWorkload]