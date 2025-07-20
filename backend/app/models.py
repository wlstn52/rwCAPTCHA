from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID
from .database import Base
from datetime import datetime

# 데이터베이스로 이미지를 관리하기 위한 모델, 이미지 저장시 uuid를 통해 저장 -> 이미지 id만 보고서 종류 추론 막기 위함
class ImagePath(Base):
    __tablename__ = "image_paths"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID, nullable=False)
    path = Column(String, nullable=False)
    label = Column(String, nullable=False)
    source = Column(String)
    

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    is_correct = Column(Boolean, default=False)
    selected_indices = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

