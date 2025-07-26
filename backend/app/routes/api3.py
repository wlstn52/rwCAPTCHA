# api.py
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from .. import crud, database, models
from ..schemas import schemas_third as schemas

router = APIRouter(prefix="/third")


# DB 세션 의존성 주입
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/question", response_model=schemas.QuestionInfo)
async def get_question(db: Session = Depends(get_db)):
    # 데이터베이스에서 모든 고유한 분류된 카테고리 가져오기
    db_categories = db.query(models.ImagePath.label) \
        .filter(models.ImagePath.label != "unclassified") \
        .distinct().all()
    all_classified_categories = [cat[0] for cat in db_categories]

    if not all_classified_categories:
        raise HTTPException(status_code=500, detail="No classified categories found in database for questions.")

    unclassified_images = crud.get_unclassified_random_images(db=db, num=1)

    num_classified_to_fetch = 16 - len(unclassified_images)
    classified_images = crud.get_classified_random_images(db=db, num=num_classified_to_fetch,
                                                          exclude_categories=["unclassified"])

    all_selected_images = unclassified_images + classified_images
    random.shuffle(all_selected_images)

    images_for_frontend = [
        schemas.ImageInfo(url=img.path, index=i, uuid=str(img.uuid))
        for i, img in enumerate(all_selected_images)
    ]

    return schemas.QuestionInfo(
        images=images_for_frontend
    )


@router.post("/submit", response_model=schemas.ResultOut)
async def submit(payload: schemas.ResultIn, db: Session = Depends(get_db)):
    db_categories = [i[0] for i in db.query(models.ImagePath.label) \
    .filter(models.ImagePath.label != "unclassified") \
    .distinct().all()]
    images_uuids_from_payload = [i.uuid for i in payload.images]

    # payload에 있는 모든 이미지의 DB 데이터를 한 번에 가져옵니다.
    image_data_from_db = crud.get_image_data(db=db, image_uuids=images_uuids_from_payload)
    correct_category_count = {i:0 for i in db_categories}
    for i in image_data_from_db:
        if i.label != 'unclassified': correct_category_count[i.label] += 1
    
    # 분류 안 된 이미지는 1개뿐 => 1개 더 많은 카테고리로 라벨링
    error_count = 0
    unclassified_category = ''
    for i in payload.answers:
        error_count += abs(correct_category_count[i.category] - i.amount) 
        if correct_category_count[i.category] +1 == i.amount:
            unclassified_category = i.category

    is_correct = error_count <= 1

    # 메인 캡챠가 정답인 경우에만 결과 및 미분류 이미지 피드백을 저장
    if is_correct:
        # 사용자가 선택한 이미지들 중 'unclassified' 이미지가 있다면 피드백 저장
        for index, img in enumerate(payload.images):
            if image_data_from_db[index].label == "unclassified":
                # 이 미분류 이미지가 사용자에 의해 'category_asked' 카테고리와 함께 선택되었다고 기록
                crud.save_unclassified_feedback(db, image_data_from_db[index].uuid, unclassified_category)
    return schemas.ResultOut(is_correct=is_correct)