# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uuid
from . import models

def get_image_data(db:Session, image_uuids: List[str]):
    return [db.query(models.ImagePath).filter(models.ImagePath.uuid == uuid.UUID(i)).first() for i in image_uuids]

def get_image_path(db: Session, id: int):
    _path = db.query(models.ImagePath).filter(models.ImagePath.id == id).first()
    if _path is None: raise ValueError("존재하지 않는 이미지")
    return _path

def get_random_images(db: Session, num: int):
    print("test")
    return db.query(models.ImagePath).order_by(func.random()).limit(num).all()

# 추가: 특정 카테고리를 제외하고 랜덤 이미지 가져오기 (주로 'unclassified' 제외)
def get_classified_random_images(db: Session, num: int, exclude_categories: List[str] = None):
    query = db.query(models.ImagePath)
    if exclude_categories:
        query = query.filter(models.ImagePath.label.notin_(exclude_categories))
    return query.order_by(func.random()).limit(num).all()

# 추가: 미분류 이미지만 랜덤으로 가져오기
def get_unclassified_random_images(db: Session, num: int):
    return db.query(models.ImagePath).filter(models.ImagePath.label == "unclassified").order_by(func.random()).limit(num).all()

def save_result(db: Session, selected: list, is_correct: bool, category_asked: str): # category_asked 추가
    db_result = models.Result(
        selected_indices=','.join(map(str, selected)),
        is_correct=is_correct,
        category_asked=category_asked # category_asked 저장
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result