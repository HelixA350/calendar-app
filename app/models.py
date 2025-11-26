from datetime import date
from typing import List
from pydantic import BaseModel


class EmployeeInfo(BaseModel):
    id: int
    full_name: str


class CalendarEvent(BaseModel):
    type: str  # "vacation" or "business_trip"
    start: date
    end: date


class DailyWorkload(BaseModel):
    date: date
    percent: float


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