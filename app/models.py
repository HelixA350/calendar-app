from datetime import date
from typing import List
from pydantic import BaseModel
from typing import Literal


class EmployeeInfo(BaseModel):
    id: int
    full_name: str


class CalendarEvent(BaseModel):
    type: Literal['vacation', 'business_trip']  # "vacation" or "business_trip"
    start: date
    end: date


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