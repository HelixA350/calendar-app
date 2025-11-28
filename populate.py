# populate.py
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import (
    engine,
    Base,
    Employee,
    CalendarEvent,
    DailyWorkload,
    SessionLocal,
    create_tables
)

def populate_db():
    # Создаём таблицы, если ещё не созданы
    create_tables()
    
    db: Session = SessionLocal()
    try:
        # Очищаем таблицы (опционально, для повторного запуска)
        db.query(DailyWorkload).delete()
        db.query(CalendarEvent).delete()
        db.query(Employee).delete()
        db.commit()

        # Добавляем 5 сотрудников
        employees_data = [
            "Иванов Иван Иванович",
            "Петрова Анна Сергеевна",
            "Сидоров Дмитрий Алексеевич",
            "Кузнецова Елена Владимировна",
            "Морозов Артём Олегович"
        ]
        employees = []
        for name in employees_data:
            emp = Employee(full_name=name)
            db.add(emp)
            employees.append(emp)
        db.commit()

        # Обновляем объекты, чтобы получить ID
        for emp in employees:
            db.refresh(emp)

        # Пример событий календаря (отпуска и командировки)
        events_data = [
            (employees[0].id, 'vacation', date(2025, 7, 1), date(2025, 7, 14)),
            (employees[1].id, 'business_trip', date(2025, 6, 10), date(2025, 6, 15)),
            (employees[2].id, 'vacation', date(2025, 8, 5), date(2025, 8, 20)),
        ]
        for emp_id, ev_type, start, end in events_data:
            event = CalendarEvent(
                employee_id=emp_id,
                event_type=ev_type,
                start_date=start,
                end_date=end
            )
            db.add(event)
        db.commit()

        # Пример ежедневной загрузки (только рабочие дни, не в отпуске и не в командировке)
        today = date.today()
        for emp in employees:
            for i in range(30):  # последние 30 дней
                work_date = today - timedelta(days=i)
                # Пропускаем выходные (суббота=5, воскресенье=6)
                if work_date.weekday() >= 5:
                    continue
                # Для простоты назначим равномерную загрузку ~80%
                workload = DailyWorkload(
                    employee_id=emp.id,
                    date=work_date,
                    percent=80.0
                )
                db.add(workload)
        db.commit()

        print("База данных успешно заполнена тестовыми данными.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при заполнении базы данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()