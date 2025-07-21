import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from .. import schemas, crud, database

router = APIRouter()

# 백엔드에만 존재하는 전체 이미지 데이터 (각 이미지의 URL과 실제 레이블 포함)
# 실제 프로젝트에서는 이 정보를 데이터베이스에서 관리하는 것이 일반적입니다.
ALL_IMAGES_DATA = [
    {"url": "/img/1.png", "label": "cardboard"},
    {"url": "/img/2.png", "label": "cardboard"},
    {"url": "/img/3.png", "label": "cardboard"},
    {"url": "/img/4.png", "label": "metal"},
    {"url": "/img/5.png", "label": "glass"},
    {"url": "/img/6.png", "label": "trash"},
    {"url": "/img/7.png", "label": "metal"},
    {"url": "/img/8.png", "label": "trash"},
    {"url": "/img/9.png", "label": "trash"},
    # 필요하다면 더 많은 이미지 추가 (각 카테고리별로 적어도 2개 이상 권장)
]

# 모든 가능한 카테고리
ALL_CATEGORIES = list(set(img["label"] for img in ALL_IMAGES_DATA))

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
    if not ALL_CATEGORIES:
        raise HTTPException(status_code=500, detail="No categories defined for questions.")

    # 무작위로 질문 카테고리 하나를 선택
    target_category = random.choice(ALL_CATEGORIES)

    random_images = crud.get_random_images(db=db, num=9)
    images_for_frontend = [
        schemas.ImageInfo(url=img.path, index=i, uuid=str(img.uuid))
        for i, img in enumerate(random_images)
    ]

    return schemas.QuestionInfo(
        category=target_category,
        images=images_for_frontend
    )

# 기존 제출 엔드포인트 수정
@router.post("/submit", response_model=schemas.ResultOut)
async def submit_selection(payload: schemas.ResultIn, db: Session = Depends(get_db)):
    selected_indices_set = set(payload.selected)
    category_asked = payload.category_asked # 프론트엔드에서 전달받은 질문 카테고리
    images = [i.uuid for i in payload.images]

    image_data = crud.get_image_data(db=db, image_uuids=images)

    # 백엔드에 있는 ALL_IMAGES_DATA를 기반으로 해당 카테고리의 정답 인덱스를 찾습니다.
    correct_indices_for_category = {
        i for i, img in enumerate(image_data)
        if img.label == category_asked
    }

    # 사용자의 선택과 실제 정답을 비교
    is_correct = (selected_indices_set == correct_indices_for_category)

    # 결과 저장 (selected_indices는 사용자가 선택한 원본 인덱스를 그대로 저장), 일단 보류: 아직 학습 못한 이미지 없음
    #crud.save_result(db, payload.selected, is_correct)

    return schemas.ResultOut(is_correct=is_correct)