# api.py
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from .. import schemas, crud, database, models  # models import 추가

router = APIRouter()


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
    # 'unclassified'는 질문 카테고리로는 사용하지 않습니다.
    db_categories = db.query(models.ImagePath.label) \
        .filter(models.ImagePath.label != "unclassified") \
        .distinct().all()
    all_classified_categories = [cat[0] for cat in db_categories]

    if not all_classified_categories:
        raise HTTPException(status_code=500, detail="No classified categories found in database for questions.")

    # 무작위로 질문 카테고리 하나를 선택 (분류된 카테고리 중에서)
    target_category = random.choice(all_classified_categories)

    # 미분류 이미지 3개 가져오기
    unclassified_images = crud.get_unclassified_random_images(db=db, num=3)

    # 미분류 이미지가 3개 미만인 경우 예외 처리 (선택 사항)
    if len(unclassified_images) < 3:
        # 이 경우, 오류를 발생시키거나, 미분류 이미지 대신 분류된 이미지를 더 가져오는 등의 로직 추가 가능
        print("경고: 미분류 이미지가 3개 미만입니다. 현재는 있는 이미지만 사용합니다.")

    # 분류된 이미지 가져오기 (총 9개 - 현재 미분류 이미지 수)
    num_classified_to_fetch = 9 - len(unclassified_images)
    classified_images = crud.get_classified_random_images(db=db, num=num_classified_to_fetch,
                                                          exclude_categories=["unclassified"])

    # 미분류 이미지와 분류된 이미지를 합치고 섞습니다.
    all_selected_images = unclassified_images + classified_images
    random.shuffle(all_selected_images)  # 이미지를 무작위로 섞어줍니다.

    images_for_frontend = [
        schemas.ImageInfo(url=img.path, index=i, uuid=str(img.uuid))
        for i, img in enumerate(all_selected_images)  # 섞인 순서대로 인덱스 부여
    ]

    return schemas.QuestionInfo(
        category=target_category,
        images=images_for_frontend
    )


# 기존 제출 엔드포인트 수정
@router.post("/submit", response_model=schemas.ResultOut)
async def submit_selection(payload: schemas.ResultIn, db: Session = Depends(get_db)):
    selected_indices_set = set(payload.selected)
    category_asked = payload.category_asked  # 프론트엔드에서 전달받은 질문 카테고리
    images_uuids = [i.uuid for i in payload.images]

    image_data_from_db = crud.get_image_data(db=db, image_uuids=images_uuids)

    # 백엔드에 있는 실제 이미지 데이터(DB에서 가져온)를 기반으로 해당 카테고리의 정답 인덱스를 찾습니다.
    # 미분류 이미지는 'correct_indices_for_category' 계산에 포함되지 않습니다.
    correct_indices_for_category = set()
    for i, img_info in enumerate(payload.images):
        matched_db_image = next((db_img for db_img in image_data_from_db if str(db_img.uuid) == img_info.uuid), None)
        # 질문 카테고리와 일치하는 이미지의 인덱스만 정답으로 간주합니다.
        # 미분류 이미지(label == "unclassified")는 여기에 포함되지 않습니다.
        if matched_db_image and matched_db_image.label == category_asked:
            correct_indices_for_category.add(i)

            # 사용자가 선택한 인덱스 중 질문 카테고리에 해당하는 것만 필터링
    user_selected_classified_indices = set()
    for selected_idx in selected_indices_set:
        # payload.images는 프론트엔드에서 보낸 순서대로 이미지를 담고 있으며, 그 순서에 해당하는 인덱스를 사용
        if 0 <= selected_idx < len(payload.images):  # 인덱스 유효성 검사
            img_info = payload.images[selected_idx]
            matched_db_image = next((db_img for db_img in image_data_from_db if str(db_img.uuid) == img_info.uuid),
                                    None)
            if matched_db_image and matched_db_image.label == category_asked:
                user_selected_classified_indices.add(selected_idx)

    # 미분류 이미지를 선택하거나 안한 것이 정답 여부에 영향을 주지 않으려면,
    # 오직 질문 카테고리에 해당하는 이미지만을 비교해야 합니다.
    # 즉, 사용자가 질문 카테고리의 모든 이미지를 선택했고, 질문 카테고리가 아닌 다른 분류된 이미지를 선택하지 않았다면 정답.
    # 미분류 이미지를 선택했는지 여부는 여기서 고려하지 않습니다.
    is_correct = (user_selected_classified_indices == correct_indices_for_category)

    # 정답인 경우에만 결과 저장
    if is_correct:
        # payload.selected는 사용자가 실제로 선택한 모든 이미지의 인덱스를 포함합니다.
        # 미분류 이미지 선택 여부도 함께 저장됩니다.
        crud.save_result(db, payload.selected, is_correct, category_asked)
    # 오답인 경우 저장하지 않음 (요구사항 반영)

    return schemas.ResultOut(is_correct=is_correct)