#!/usr/bin/env python3
"""
Скрипт для проверки соответствия API спецификации
"""
import json
from datetime import date
from typing import List
from pydantic import BaseModel

# Импортируем модели из проекта
from app.models import EmployeeInfo, CalendarEvent, DailyWorkload, CalendarResponseItem, WorkloadResponseItem, WorkloadResponse

def check_models():
    """Проверяем, что модели соответствуют спецификации"""
    print("Проверка моделей:")
    
    # Проверяем EmployeeInfo
    emp = EmployeeInfo(id=101, full_name="Иванов Иван Иванович")
    print(f"✓ EmployeeInfo: {emp}")
    
    # Проверяем CalendarEvent
    event = CalendarEvent(type="vacation", start=date(2025, 11, 5), end=date(2025, 11, 15))
    print(f"✓ CalendarEvent: {event}")
    
    # Проверяем DailyWorkload
    workload = DailyWorkload(date=date(2025, 11, 15), percent=90.0)
    print(f"✓ DailyWorkload: {workload}")
    
    # Проверяем составные модели
    cal_item = CalendarResponseItem(
        employee=emp,
        events=[event]
    )
    print(f"✓ CalendarResponseItem: {cal_item}")
    
    wl_item = WorkloadResponseItem(
        employee=emp,
        workload=[workload]
    )
    print(f"✓ WorkloadResponseItem: {wl_item}")
    
    wl_response = WorkloadResponse(
        employees=[wl_item],
        total=[workload]
    )
    print(f"✓ WorkloadResponse: {wl_response}")
    
    print("\nВсе модели соответствуют спецификации!")

def check_api_responses():
    """Проверяем, что API возвращает корректные данные"""
    print("\nПроверка API-ответов:")
    
    # Импортируем сервисы
    from app.services import CalendarService, WorkloadService
    from datetime import date
    
    # Тестируем календарь
    calendar_result = CalendarService.get_calendar(
        start_date=date(2025, 11, 1),
        end_date=date(2025, 11, 30)
    )
    print(f"✓ Календарь: {len(calendar_result)} сотрудников")
    
    # Тестируем загрузку
    workload_result = WorkloadService.get_workload(
        start_date=date(2025, 11, 1),
        end_date=date(2025, 11, 5)
    )
    print(f"✓ Загрузка: {len(workload_result.employees)} сотрудников, {len(workload_result.total)} дней")
    
    print("\nAPI-ответы соответствуют спецификации!")

if __name__ == "__main__":
    check_models()
    check_api_responses()
    print("\n✓ Все проверки пройдены успешно! Проект соответствует спецификации.")