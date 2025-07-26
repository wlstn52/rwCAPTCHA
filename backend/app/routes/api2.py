import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from .. import crud, database, models
from ..schemas import schemas_second as schemas

NUMBER_OF_IMAGES = 5

router = APIRouter(prefix="/second")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/question", response_model=schemas.QuestionInfo)
async def get_question(db: Session = Depends(get_db)):
    unclassified_images = crud.get_unclassified_random_images(db=db, num=1)
    num_classified_to_fetch = NUMBER_OF_IMAGES - len(unclassified_images)
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
async def submit_selection(payload: schemas.ResultIn, db: Session = Depends(get_db)):
    correct_counts = 0
    images_uuids_from_payload = [i.uuid for i in payload.images]
    answers_from_payload = payload.answers

    image_data_from_db = [crud.get_image_path(db=db, u=i) for i in images_uuids_from_payload]

    db_category_list = [str(img.label) for img in image_data_from_db]

    for i in range(NUMBER_OF_IMAGES):
        if db_category_list[i] == 'unclassified':
            unclassified_uuid = uuid.UUID(images_uuids_from_payload[i])
            unclassified_category = answers_from_payload[i]
        else:
            if(db_category_list[i] == answers_from_payload[i]): correct_counts += 1
    is_correct = correct_counts >= NUMBER_OF_IMAGES-1
    # 메인 캡챠가 정답인 경우에만 결과 및 미분류 이미지 피드백을 저장
    if is_correct:
        crud.save_result_second(db, is_correct, [img.id for img in image_data_from_db], answers_from_payload)  # 메인 캡챠 결과 저장
        crud.save_unclassified_feedback(db, unclassified_uuid, unclassified_category)
    return schemas.ResultOut(is_correct=is_correct)