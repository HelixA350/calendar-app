from datetime import date, timedelta
from typing import List, Dict, Optional
from app.models import GetemployeeResponse, EmployeeInfo, CreateCalendarEvent, CalendarEvent as ModelCalendarEvent, DailyWorkload as ModelDailyWorkload, CalendarResponseItem, WorkloadResponseItem, WorkloadResponse, EmployeeDepInfo
from app.database import get_db, Employee, CalendarEvent, DailyWorkload, Department, History
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import CreateEmployee, CalendarEventDelete, CalendarEventUpdateDates
from sqlalchemy import and_
import requests
import os
from sqlalchemy.orm import joinedload

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
                id=event.id,
                type=event.event_type,
                start=event.start_date,
                end=event.end_date,
                level = event.level,
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
        
        employee = db.query(Employee).filter(Employee.id == event_data.employee_id).first()
        if not employee:
            raise ValueError("Сотрудник с указанным ID не найден")

        # Check for overlapping events for the same employee
        existing_events = db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.employee_id == event_data.employee_id,
                CalendarEvent.start_date <= event_data.end,
                CalendarEvent.end_date >= event_data.start,
                CalendarEvent.level == 'approved',
            )
        ).all()

        if existing_events:
            raise ValueError(f"У сотрудника уже есть согласованное событие между {event_data.start} и {event_data.end}")

        # Create new event
        db_event = CalendarEvent(
            employee_id=event_data.employee_id,
            event_type=event_data.type,
            start_date=event_data.start,
            end_date=event_data.end,
            level=event_data.level,
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return db_event
    
    @staticmethod
    def delete_event(
        db: Session, 
        delete_data: CalendarEventDelete
    ) -> bool:
        """
        Удаление события календаря по ID
        """
        # Находим событие по ID
        event = db.query(CalendarEvent).filter(
            CalendarEvent.id == delete_data.event_id
        ).first()
        
        if not event:
            return False
        
        # Удаляем событие
        db.delete(event)
        db.commit()
        
        return True
    
    @staticmethod
    def update_event(
        db: Session, 
        update_data: CalendarEventUpdateDates
    ) -> CalendarEvent:
        """
        Обновление дат события календаря, возвращает обновленное событие
        """
        # Находим событие по ID
        event = db.query(CalendarEvent).filter(
            CalendarEvent.id == update_data.event_id
        ).first()
        
        if not event:
            raise ValueError("Событие не найдено")
        
        # Определяем новые даты, используя переданные или существующие
        start_date = update_data.new_start_date or event.start_date
        end_date = update_data.new_end_date or event.end_date
        
        # Проверяем валидность
        if end_date < start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        
        # Обновляем уровень всегда, если передан
        if update_data.new_level is not None:
            event.level = update_data.new_level
        
        # Обновляем даты если изменилось
        if start_date != event.start_date or end_date != event.end_date:
            event.start_date = start_date
            event.end_date = end_date
        
        db.commit()
        db.refresh(event)
        
        return event

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
    
class EmployeeService:
    @staticmethod
    def create_employee(db: Session, employee_data: CreateEmployee) -> Employee:
        """
        METHOD IS DEPRECATED
        Создает нового сотрубника в базе данных
        """
        db_employee = Employee(
            full_name=employee_data.full_name,
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def get_employees_with_departments(db: Session, department_id: Optional[int] = None) -> GetemployeeResponse:
        query = db.query(Employee).options(joinedload(Employee.departments))

        if department_id is not None:
            # Фильтруем сотрудников, принадлежащих указанному отделу
            query = query.join(Employee.departments).filter(Department.id == department_id)

        employees = query.all()

        result = [
            EmployeeDepInfo(
                id=emp.id,
                full_name=emp.full_name,
                department_id=[dep.id for dep in emp.departments]
            )
            for emp in employees
        ]

        return GetemployeeResponse(root=result)
    
class DepartmentService:
    @staticmethod
    def get_departments(db: Session) -> List[str]:
        data = db.query(Department).all()
        return [{
            'name': item.dep_name,
            'id': item.id,
        } for item in data]
    
class BitrixService:
    def __init__(self, db: Session):
        self.db = db
    
    def sync_with_bitrix(self):
        bitrix_data = {
            'departments': self.__fetch_departments(),
            'employees': self.__fetch_employees(),
        }

        # --- Синхронизация отделов ---
        bitrix_deps_by_id = {d['id']: d for d in bitrix_data['departments']}
        db_deps = self.__get_departments_db()
        db_deps_by_id = {d['id']: d for d in db_deps}

        # Удаляем лишние отделы
        for db_id in list(db_deps_by_id.keys()):
            if db_id not in bitrix_deps_by_id:
                self.db.query(Department).filter(Department.id == db_id).delete()

        # Добавляем/обновляем отделы
        for bitrix_dep in bitrix_data['departments']:
            db_dep = self.db.query(Department).filter(Department.id == bitrix_dep['id']).first()
            if db_dep:
                if db_dep.dep_name != bitrix_dep['dep_name']:
                    db_dep.dep_name = bitrix_dep['dep_name']
            else:
                new_dep = Department(id=bitrix_dep['id'], dep_name=bitrix_dep['dep_name'])
                self.db.add(new_dep)

        # --- Синхронизация сотрудников ---
        bitrix_emps_by_id = {e['id']: e for e in bitrix_data['employees']}
        db_emps = self.__get_employees_db()
        db_emps_by_id = {e['id']: e for e in db_emps}

        # Удаляем лишних сотрудников
        for db_id in list(db_emps_by_id.keys()):
            if db_id not in bitrix_emps_by_id:
                self.db.query(Employee).filter(Employee.id == db_id).delete()

        # Обновляем/добавляем сотрудников + связи
        for bitrix_emp in bitrix_data['employees']:
            db_emp = self.db.query(Employee).options(joinedload(Employee.departments)).filter(Employee.id == bitrix_emp['id']).first()
            full_name = bitrix_emp['full_name'].strip()
            dep_ids = bitrix_emp['department_id'] or []

            if db_emp:
                if db_emp.full_name != full_name:
                    db_emp.full_name = full_name
                # Обновляем связи
                existing_dep_ids = {d.id for d in db_emp.departments}
                target_dep_ids = set(dep_ids)

                # Удаляем лишние связи
                for d in list(db_emp.departments):
                    if d.id not in target_dep_ids:
                        db_emp.departments.remove(d)

                # Добавляем недостающие связи
                for dep_id in target_dep_ids - existing_dep_ids:
                    dep = self.db.query(Department).filter(Department.id == dep_id).first()
                    if dep:
                        db_emp.departments.append(dep)
            else:
                # Создаём нового сотрудника
                new_emp = Employee(id=bitrix_emp['id'], full_name=full_name)
                self.db.add(new_emp)
                self.db.flush()  # чтобы получить id, если autoincrement (но у вас id уже задан)
                # Добавляем связи
                for dep_id in dep_ids:
                    dep = self.db.query(Department).filter(Department.id == dep_id).first()
                    if dep:
                        new_emp.departments.append(dep)

        # Фиксируем изменения
        self.db.commit()
        return {'message': 'success'}

    

    
    def __get_departments_db(self):
        data = self.db.query(Department).all()
        return [{"id": item.id, "dep_name": item.dep_name} for item in data]

    def __get_employees_db(self):
        data = self.db.query(Employee).options(joinedload(Employee.departments)).all()
        return [
            {
                "id": item.id,
                "full_name": item.full_name,
                "department_id": [d.id for d in item.departments],  # ← Вот здесь исправлено
            }
            for item in data
        ]

    def __fetch_departments(self):
        response = self.__fetch_all_data(
            url=f'https://tandem-consult.ru/rest/516/{os.getenv("BITRIX_TOKEN")}/department.get',
            total_key='total',
            data_key='result',
            params={
                "sort": "NAME",
                "order": "DESC",
            }
        )
        data = [{
            "id": int(item['ID']),
            "dep_name": item['NAME'],
        } for item in response]
        return data # Список всех отделов

    def __fetch_employees(self):
        response = self.__fetch_all_data(
            url=f'https://tandem-consult.ru/rest/516/82r9f32dxjjsar8b/user.get',
            total_key='total',
            data_key='result',
            params = {    "ADMIN_MODE": True,
                "USER_TYPE": "employee",
                "SORT": "ID",
                "ORDER": "asc",
                "ACTIVE": True,
            },
        )
        data = [{
            "id": int(item.get('ID')),
            "full_name": f"{item.get('LAST_NAME')} {item.get('NAME')} {item.get('SECOND_NAME')}",
            "department_id": item['UF_DEPARTMENT'] if item['UF_DEPARTMENT'] else []
        } for item in response]
        return data # Список всех сотрудников

    def __fetch_all_data(self, url, params: dict, total_key='total', next_key='next', data_key='items', ):
        all_data = []
        start = 0

        while True:
            params = params.copy()
            params['start'] = start
            resp = requests.post(url, json=params)
            resp.raise_for_status()
            data = resp.json()

            records = data[data_key]
            all_data.extend(records)

            total = data[total_key]
            if len(all_data) >= total:
                break

            start = data.get(next_key)
            if start is None:
                break

        return all_data
    

class AuthService:
    @staticmethod
    def check_role(token, app):
        try:
            response = requests.get(
                'http://10.100.50.37:8125/check_role', # HARDCODE - адрес сервиса авторизации
                params={'auth_token': token, 'app_name': app}
            )
            response.raise_for_status()
            return response.json().get('role')
        except requests.exceptions.RequestException:
            raise ValueError("Failed to check role")
        

class HistoryService:
    @staticmethod
    def get_history(db: Session, employee_id: int):
        history_entries = db.query(History).filter(History.employee_id == employee_id).all()
        result = []
        for entry in history_entries:
            result.append({
                'event_type': entry.event_type,
                'date': entry.date,
                'verdict': entry.verdict,
                'level': entry.level,
                'participant': {
                    'id': entry.participant.id,
                    'full_name': entry.participant.full_name
                } if entry.participant else None
            })
        return result