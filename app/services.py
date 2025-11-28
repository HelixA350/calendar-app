from datetime import date, timedelta
from typing import List, Dict, Optional
from app.models import EmployeeInfo, CreateCalendarEvent, CalendarEvent as ModelCalendarEvent, DailyWorkload as ModelDailyWorkload, CalendarResponseItem, WorkloadResponseItem, WorkloadResponse
from app.database import get_db, Employee, CalendarEvent, DailyWorkload
from sqlalchemy.orm import Session
from sqlalchemy import and_





class CalendarService:
    @staticmethod
    def get_calendar(db: Session, start_date: date, end_date: date) -> List[CalendarResponseItem]:
        """
        Get calendar events for the specified date range from the database
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Query events that overlap with the date range
        db_events = db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_date <= end_date,
                CalendarEvent.end_date >= start_date
            )
        ).all()
        
        result = []
        
        # Group events by employee
        employee_events = {}
        for event in db_events:
            employee = event.employee
            if employee.id not in employee_events:
                employee_events[employee.id] = {
                    'employee': EmployeeInfo(id=employee.id, full_name=employee.full_name),
                    'events': []
                }
            
            # Convert database event to model event
            model_event = ModelCalendarEvent(
                type=event.event_type,
                start=event.start_date,
                end=event.end_date
            )
            employee_events[employee.id]['events'].append(model_event)
        
        # Create response items
        for emp_data in employee_events.values():
            result.append(CalendarResponseItem(
                employee=emp_data['employee'],
                events=emp_data['events']
            ))
        
        return result

    @staticmethod
    def create_event(db: Session, event_data: CreateCalendarEvent) -> CalendarEvent:
        """
        Create a new calendar event in the database
        """
        # Validate date range
        if event_data.start > event_data.end:
            raise ValueError("Start date cannot be after end date")

        # Check for overlapping events for the same employee
        existing_events = db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.employee_id == event_data.employee_id,
                CalendarEvent.start_date <= event_data.end,
                CalendarEvent.end_date >= event_data.start
            )
        ).all()

        if existing_events:
            raise ValueError(f"Employee already has an event during this period: {event_data.start} to {event_data.end}")

        # Create new event
        db_event = CalendarEvent(
            employee_id=event_data.employee_id,
            event_type=event_data.type,
            start_date=event_data.start,
            end_date=event_data.end
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return db_event
class WorkloadService:
    @staticmethod
    def get_workload(db: Session, start_date: date, end_date: date) -> WorkloadResponse:
        """
        Get daily workload for employees in the specified date range from the database
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Calculate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date = current_date + timedelta(days=1)
        
        # Get all employees with their workload entries for the date range
        db_workloads = db.query(DailyWorkload).filter(
            DailyWorkload.date >= start_date,
            DailyWorkload.date <= end_date
        ).all()
        
        # Group workload entries by employee
        employee_workloads = {}
        for workload in db_workloads:
            employee = workload.employee
            emp_id = employee.id
            if emp_id not in employee_workloads:
                employee_workloads[emp_id] = {
                    'employee': EmployeeInfo(id=employee.id, full_name=employee.full_name),
                    'workload': {}
                }
            
            # Store workload by date
            employee_workloads[emp_id]['workload'][workload.date] = workload.percent
        
        # Build response for each employee
        employees_workload = []
        for emp_id, emp_data in employee_workloads.items():
            # Create workload entries for each date in range
            workload_entries = []
            for date_entry in date_range:
                percent = emp_data['workload'].get(date_entry, 0.0)
                workload_entries.append(ModelDailyWorkload(date=date_entry, percent=percent))
            
            # Sort by date
            workload_entries.sort(key=lambda x: x.date)
            
            employees_workload.append(WorkloadResponseItem(
                employee=emp_data['employee'],
                workload=workload_entries
            ))
        
        # Calculate total workload for each date
        total_workload = []
        for date_entry in date_range:
            total_percent = 0.0
            valid_entries = 0
            
            # Count valid workload entries for this date
            for workload in db_workloads:
                if workload.date == date_entry:
                    total_percent += workload.percent
                    valid_entries += 1
            
            if valid_entries > 0:
                avg_percent = total_percent / valid_entries
                total_workload.append(ModelDailyWorkload(date=date_entry, percent=avg_percent))
            else:
                total_workload.append(ModelDailyWorkload(date=date_entry, percent=0.0))
        
        # Sort total workload by date
        total_workload.sort(key=lambda x: x.date)
        
        return WorkloadResponse(employees=employees_workload, total=total_workload)