from datetime import date, timedelta
from typing import List, Dict, Optional
from app.models import EmployeeInfo, CalendarEvent, DailyWorkload, CalendarResponseItem, WorkloadResponseItem, WorkloadResponse


# Mock data storage (in a real application, this would be a database)
MOCK_EMPLOYEES = [
    EmployeeInfo(id=101, full_name="Иванов Иван Иванович"),
    EmployeeInfo(id=102, full_name="Петрова Анна Сергеевна"),
    EmployeeInfo(id=103, full_name="Сидоров Сергей Петрович"),
]

MOCK_CALENDAR_EVENTS = [
    {
        "employee_id": 101,
        "events": [
            CalendarEvent(type="vacation", start=date(2025, 11, 5), end=date(2025, 11, 12)),
            CalendarEvent(type="business_trip", start=date(2025, 11, 18), end=date(2025, 11, 22)),
        ]
    },
    {
        "employee_id": 102,
        "events": [
            CalendarEvent(type="vacation", start=date(2025, 11, 10), end=date(2025, 11, 20)),
            CalendarEvent(type="business_trip", start=date(2025, 11, 25), end=date(2025, 11, 28)),
        ]
    },
    {
        "employee_id": 103,
        "events": [
            CalendarEvent(type="vacation", start=date(2025, 11, 15), end=date(2025, 11, 25)),
        ]
    }
]

MOCK_WORKLOADS = [
    {
        "employee_id": 101,
        "workload": [
            DailyWorkload(date=date(2025, 11, 1), percent=100.0),
            DailyWorkload(date=date(2025, 11, 2), percent=100.0),
            DailyWorkload(date=date(2025, 11, 3), percent=0.0),
            DailyWorkload(date=date(2025, 11, 4), percent=80.0),
            DailyWorkload(date=date(2025, 11, 5), percent=80.0),
        ]
    },
    {
        "employee_id": 102,
        "workload": [
            DailyWorkload(date=date(2025, 11, 1), percent=90.0),
            DailyWorkload(date=date(2025, 11, 2), percent=90.0),
            DailyWorkload(date=date(2025, 11, 3), percent=0.0),
            DailyWorkload(date=date(2025, 11, 4), percent=100.0),
            DailyWorkload(date=date(2025, 11, 5), percent=100.0),
        ]
    },
    {
        "employee_id": 103,
        "workload": [
            DailyWorkload(date=date(2025, 11, 1), percent=75.0),
            DailyWorkload(date=date(2025, 11, 2), percent=75.0),
            DailyWorkload(date=date(2025, 11, 3), percent=50.0),
            DailyWorkload(date=date(2025, 11, 4), percent=90.0),
            DailyWorkload(date=date(2025, 11, 5), percent=90.0),
        ]
    }
]


class CalendarService:
    @staticmethod
    def get_calendar(start_date: date, end_date: date) -> List[CalendarResponseItem]:
        """
        Get calendar events for the specified date range
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        result = []
        
        for emp_events in MOCK_CALENDAR_EVENTS:
            employee_id = emp_events["employee_id"]
            employee = next((emp for emp in MOCK_EMPLOYEES if emp.id == employee_id), None)
            if not employee:
                continue
                
            # Filter events that fall within the requested date range
            filtered_events = []
            for event in emp_events["events"]:
                # Check if event overlaps with the requested date range
                if event.start <= end_date and event.end >= start_date:
                    filtered_events.append(event)
            
            if filtered_events:
                result.append(CalendarResponseItem(
                    employee=employee,
                    events=filtered_events
                ))
        
        return result


class WorkloadService:
    @staticmethod
    def get_workload(start_date: date, end_date: date) -> WorkloadResponse:
        """
        Get daily workload for employees in the specified date range
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Calculate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date = current_date + timedelta(days=1)
        
        employees_workload = []
        total_workload = []
        
        for emp_workload in MOCK_WORKLOADS:
            employee_id = emp_workload["employee_id"]
            employee = next((emp for emp in MOCK_EMPLOYEES if emp.id == employee_id), None)
            if not employee:
                continue
                
            # Filter workload entries within the requested date range
            filtered_workload = []
            for workload_entry in emp_workload["workload"]:
                if start_date <= workload_entry.date <= end_date:
                    filtered_workload.append(workload_entry)
            
            # Fill in missing dates with 0% if needed
            for date_entry in date_range:
                if not any(wl.date == date_entry for wl in filtered_workload):
                    filtered_workload.append(DailyWorkload(date=date_entry, percent=0.0))
            
            # Sort by date
            filtered_workload.sort(key=lambda x: x.date)
            
            employees_workload.append(WorkloadResponseItem(
                employee=employee,
                workload=filtered_workload
            ))
        
        # Calculate total workload for each date
        for date_entry in date_range:
            total_percent = 0.0
            valid_entries = 0
            
            for emp_workload in MOCK_WORKLOADS:
                for workload_entry in emp_workload["workload"]:
                    if workload_entry.date == date_entry:
                        total_percent += workload_entry.percent
                        valid_entries += 1
                        break  # Only count once per employee
            
            if valid_entries > 0:
                avg_percent = total_percent / valid_entries if valid_entries > 0 else 0.0
                total_workload.append(DailyWorkload(date=date_entry, percent=avg_percent))
            else:
                total_workload.append(DailyWorkload(date=date_entry, percent=0.0))
        
        # Sort total workload by date
        total_workload.sort(key=lambda x: x.date)
        
        return WorkloadResponse(employees=employees_workload, total=total_workload)