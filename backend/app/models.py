from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base
from datetime import datetime

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    is_correct = Column(Boolean, default=False)
    selected_indices = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)