# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship  # relationship import 추가
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

    # UnclassifiedFeedback과의 관계 정의 (선택 사항이지만 유용)
    feedback_entries = relationship("UnclassifiedFeedback", back_populates="image_path_ref")


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    is_correct = Column(Boolean, default=False)
    selected_indices = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category_asked = Column(String, nullable=False)

class ResultSecond(Base):
    __tablename__ = "results_second"
    id = Column(Integer, primary_key=True, index=True)
    is_correct = Column(Boolean, default=False)
    asked_questions = Column(String)
    selected_answers = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# 추가: 미분류 이미지에 대한 사용자 피드백을 저장하는 테이블
class UnclassifiedFeedback(Base):
    __tablename__ = "unclassified_feedback"
    id = Column(Integer, primary_key=True, index=True)
    image_uuid = Column(UUID, ForeignKey("image_paths.uuid"), nullable=False)  # 어떤 미분류 이미지인지
    user_assigned_label = Column(String, nullable=False)  # 사용자가 어떤 카테고리 질문에 이 미분류 이미지를 선택했는지
    timestamp = Column(DateTime, default=datetime.utcnow)
    # 메인 캡챠가 정답이었을 때만 저장되므로 항상 True가 될 것이지만 명시적으로 포함
    is_correct_main_captcha = Column(Boolean, default=True, nullable=False)

    # ImagePath와의 관계 정의
    image_path_ref = relationship("ImagePath", back_populates="feedback_entries")