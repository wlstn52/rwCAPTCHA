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

def save_result(db: Session, selected: list, is_correct: bool):
    db_result = models.Result(
        selected_indices=','.join(map(str, selected)),
        is_correct=is_correct
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result