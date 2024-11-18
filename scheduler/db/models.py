from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Routine(Base):
    __tablename__ = 'routines'
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(300))
    description = Column("description", Text)
    status = Column("status", String(300), default="waiting")
    # current_task = relationship("Task")

    # Foreign key for the current task
    # current_task_id = Column(Integer, ForeignKey('tasks.id'))
    
    # # Set up a relationship for the single current task
    # current_task = relationship("Task", foreign_keys=[current_task_id])

    created_at = Column("created_at", DateTime, default=datetime.now)
    updated_at = Column("updated_at", DateTime, default=datetime.now)
    # condition_function = Column("condition_function", String(300))
    # condition_function_args = Column("condition_function_args", String(300))
    retry_delay = Column("retry_delay", Integer, default=5*60)
    retry_limit = Column("retry_limit", Integer, default=5)
    error = Column("error", Text, default="")
    tasks = relationship("Task", back_populates="routine")

    def __init__(
            self, 
            name: str, 
            description: str, 
            # condition_function: str = None,
            # condition_function_args: str = None,
            retry_delay: int = 5*60,
            retry_limit: int = 5
        ) -> None:
        self.name = name
        self.description = description
        # self.condition_function = condition_function
        # self.condition_function_args = condition_function_args
        self.retry_delay = retry_delay
        self.retry_limit = retry_limit

    def __repr__(self) -> str:
        return f"<Routine | {self.name} | {self.status}>"
    


class Task(Base):
    __tablename__ = 'tasks'
    id = Column("id", Integer, primary_key=True)
    routine_id = Column("routine_id", Integer, ForeignKey('routines.id'))
    routine = relationship("Routine", back_populates="tasks")
    status = Column("status", String(300), default="pending")
    error = Column("error", Text, default="")
    created_at = Column("created_at", DateTime, default=datetime.now)
    updated_at = Column("updated_at", DateTime, default=datetime.now)
    completed_at = Column("completed_at", DateTime)

    def __init__(
            self, 
            routine: Routine,
            status: str = "pending", 
            error: str = "", 
            completed_at: datetime = None
        ) -> None:
        self.routine_id = Routine.id
        self.routine = routine
        self.status = status
        self.error = error
        self.completed_at = completed_at
                
    def __repr__(self) -> str:
        return f"<Task | {self.routine_id} | {self.status} | {self.routine.id}:{self.routine.name}>"


    