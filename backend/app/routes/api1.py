# api.py
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from .. import crud, database, models
from ..schemas import schemas_first as schemas

router = APIRouter(prefix="/first")


# DB 세션 의존성 주입
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 새 엔드포인트: 특정 질문 카테고리와 함께 이미지를 반환
@router.get("/question", response_model=schemas.QuestionInfo)
async def get_question(db: Session = Depends(get_db)):
    # 데이터베이스에서 모든 고유한 분류된 카테고리 가져오기
    db_categories = db.query(models.ImagePath.label) \
        .filter(models.ImagePath.label != "unclassified") \
        .distinct().all()
    all_classified_categories = [cat[0] for cat in db_categories]

    if not all_classified_categories:
        raise HTTPException(status_code=500, detail="No classified categories found in database for questions.")

    target_category = random.choice(all_classified_categories)

    unclassified_images = crud.get_unclassified_random_images(db=db, num=3)

    if len(unclassified_images) < 3:
        # 미분류 이미지가 3개 미만인 경우, 오류를 발생시키거나
        # 또는 부족한 만큼 분류된 이미지를 더 가져오는 등의 유연한 로직을 추가할 수 있습니다.
        # 여기서는 경고만 출력하고 현재 있는 미분류 이미지만 사용합니다.
        print(f"경고: 데이터베이스에 미분류 이미지가 {len(unclassified_images)}개 밖에 없습니다. 3개를 채우지 못했습니다.")

    num_classified_to_fetch = 9 - len(unclassified_images)
    classified_images = crud.get_classified_random_images(db=db, num=num_classified_to_fetch,
                                                          exclude_categories=["unclassified"])

    all_selected_images = unclassified_images + classified_images
    random.shuffle(all_selected_images)

    images_for_frontend = [
        schemas.ImageInfo(url=img.path, index=i, uuid=str(img.uuid))
        for i, img in enumerate(all_selected_images)
    ]

    return schemas.QuestionInfo(
        category=target_category,
        images=images_for_frontend
    )


@router.post("/submit", response_model=schemas.ResultOut)
async def submit_selection(payload: schemas.ResultIn, db: Session = Depends(get_db)):
    selected_indices_set = set(payload.selected)
    category_asked = payload.category_asked
    images_uuids_from_payload = [i.uuid for i in payload.images]

    # payload에 있는 모든 이미지의 DB 데이터를 한 번에 가져옵니다.
    image_data_from_db = crud.get_image_data(db=db, image_uuids=images_uuids_from_payload)

    # UUID를 키로, DB 이미지 객체를 값으로 하는 맵을 만들어 효율적인 조회를 가능하게 합니다.
    db_image_map = {str(img.uuid): img for img in image_data_from_db}

    correct_indices_for_category = set()
    for i, img_info_from_payload in enumerate(payload.images):
        db_img = db_image_map.get(img_info_from_payload.uuid)
        if db_img and db_img.label == category_asked:
            correct_indices_for_category.add(i)

    user_selected_classified_indices = set()
    for selected_idx in selected_indices_set:
        if 0 <= selected_idx < len(payload.images):
            img_info_from_payload = payload.images[selected_idx]
            db_img = db_image_map.get(img_info_from_payload.uuid)
            if db_img and db_img.label == category_asked:  # 선택된 이미지 중 질문 카테고리와 일치하는 것만
                user_selected_classified_indices.add(selected_idx)

    is_correct = (user_selected_classified_indices == correct_indices_for_category)

    # 메인 캡챠가 정답인 경우에만 결과 및 미분류 이미지 피드백을 저장
    if is_correct:
        crud.save_result(db, [img.id for img in image_data_from_db], is_correct, category_asked)  # 메인 캡챠 결과 저장 // 이미지의 데이터베이스상의 id가 저장되도록 수정

        # 사용자가 선택한 이미지들 중 'unclassified' 이미지가 있다면 피드백 저장
        for selected_idx in selected_indices_set:
            if 0 <= selected_idx < len(payload.images):
                img_info_from_payload = payload.images[selected_idx]
                db_img = db_image_map.get(img_info_from_payload.uuid)

                if db_img and db_img.label == "unclassified":
                    # 이 미분류 이미지가 사용자에 의해 'category_asked' 카테고리와 함께 선택되었다고 기록
                    crud.save_unclassified_feedback(db, db_img.uuid, category_asked)
    # 오답인 경우 아무것도 저장하지 않음 (이전 요구사항 유지)

    return schemas.ResultOut(is_correct=is_correct)