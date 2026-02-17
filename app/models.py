from datetime import date
from typing import List
from pydantic import BaseModel, RootModel
from typing import Literal, Optional

class EmployeeInfo(BaseModel):
    id: int
    full_name: str

class CreateEmployee(BaseModel):
    full_name: str

class CreateEmployeeResponse(BaseModel):
    id: int


class CalendarEvent(BaseModel):
    id: int
    type: Literal['vacation', 'business_trip']  # "vacation" or "business_trip"
    start: date
    end: date
    level: str

class CalendarEventDelete(BaseModel):
    event_id: int

class UpdateCalendarEventDates(BaseModel):
    new_start_date: Optional[date] = None
    new_end_date: Optional[date] = None
    new_level: Optional[Literal['saved', 'approved']] = None

class CalendarEventUpdateDates(BaseModel):
    event_id: int
    new_start_date: Optional[date] = None
    new_end_date: Optional[date] = None
    new_level: Optional[Literal['saved', 'approved']] = None

class DeleteEventResponse(BaseModel):
    message: str = 'Событие успешно удалено'
    event_id: int

class UpdateEventResponse(BaseModel):
    event_id: int
    status: str = 'Данные о событии успешно обновлены'
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
    level: Literal['saved', 'approved'] = 'saved'

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

class DepartmentInfo(BaseModel):
    id: int
    name: str

class DepartmentsResponse(RootModel):
    root: List[DepartmentInfo]

class EmployeeDepInfo(BaseModel):
    id: int
    full_name: str
    department_id: List[int]

class GetemployeeResponse(RootModel):
    root: List[EmployeeDepInfo]

class AuthToken(BaseModel):
    auth_token: str
    app_name: str
