from sqlalchemy.orm import Session
from . import models

def save_result(db: Session, selected: list, is_correct: bool):
    db_result = models.Result(
        selected_indices=','.join(map(str, selected)),
        is_correct=is_correct
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result