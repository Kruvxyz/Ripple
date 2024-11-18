from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Message(Base):
    __tablename__ = 'queue'
    id = Column("id", Integer, primary_key=True)
    sender = Column("sender", String(300))
    routine = Column("routine", String(300))
    command = Column("command", String(300))
    timestamp = Column("timestamp", DateTime, default=datetime.now)
    status = Column("status", String(300), default="pending")
    error = Column("error", Text, default="")
    response = Column("response", Text, default="")
    # routine_id = Column("routine_id", Integer, ForeignKey("routine.id"))

    def __init__(
            self, 
            sender: str, 
            routine: str, 
            command: str, 
            status: str = "pending", 
            error: str = "", 
            response: str = "", 
            # routine_id: int = None,
        ) -> None:
        self.sender = sender
        self.routine = routine
        self.command = command
        self.status = status
        self.error = error
        self.response = response
        # self.routine_id = routine_id

    def __repr__(self) -> str:
        return f"<Message | {self.sender} | {self.routine} | {self.command} | {self.status}>"

