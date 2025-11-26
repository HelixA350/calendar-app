from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date
import os

# Create base class for declarative models
Base = declarative_base()

# -- Database models --
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    
    # Relationships
    calendar_events = relationship("CalendarEvent", back_populates="employee")
    daily_workloads = relationship("DailyWorkload", back_populates="employee")


class CalendarEvent(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    event_type = Column(String, nullable=False)  # 'vacation' or 'business_trip'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
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


# -- Database setup --
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workload_calendar.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)