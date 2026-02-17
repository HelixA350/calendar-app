from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, UniqueConstraint, ARRAY, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date
import os

# Create base class for declarative models
Base = declarative_base()

# -- Database models --
employee_department = Table(
    'employee_department', Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)
)

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)

    # Many-to-many связь с Department через промежуточную таблицу
    departments = relationship(
        "Department",
        secondary=employee_department,
        back_populates="employees"
    )

    calendar_events = relationship("CalendarEvent", back_populates="employee")
    daily_workloads = relationship("DailyWorkload", back_populates="employee")

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    dep_name = Column(String, nullable=False)

    employees = relationship(
        "Employee",
        secondary=employee_department,
        back_populates="departments"
    )


class CalendarEvent(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    event_type = Column(String, nullable=False)  # 'vacation' or 'business_trip'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    level = Column(String, nullable=False, default='saved')
    
    # Relationship
    employee = relationship("Employee", back_populates="calendar_events")


class DailyWorkload(Base):
    __tablename__ = 'daily_workloads'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    percent = Column(Float, nullable=False)  # 0.0 to 100.0

    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='unique_employee_date'),
    ) # Нельзя два раза в день работать
    
    # Relationship
    employee = relationship("Employee", back_populates="daily_workloads")


class History(Base):
    __tablename__ = 'history'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    event_type = Column(String, nullable=False)  # 'vacation' or 'business_trip'
    date = Column(Date, nullable=False)
    verdict = Column(Integer, nullable=False)  # 1 approve, 0 reject, -1 pending
    level = Column(String, nullable=False)
    participant_id = Column(Integer, ForeignKey('employees.id'), nullable=True)

    # Relationship
    employee = relationship("Employee", back_populates="history")
    participant = relationship("Employee", foreign_keys=[participant_id])


# -- Database setup --
DATABASE_URL = "postgresql://user:password@postgres:5432/db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)