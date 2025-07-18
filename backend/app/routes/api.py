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
async def get_question():
    if not ALL_CATEGORIES:
        raise HTTPException(status_code=500, detail="No categories defined for questions.")

    # 무작위로 질문 카테고리 하나를 선택
    target_category = random.choice(ALL_CATEGORIES)

    # 모든 이미지 데이터를 ImageInfo 스키마에 맞게 변환 (URL과 인덱스만 포함)
    # 이 리스트는 프론트엔드에 전달될 전체 게임 이미지 목록입니다.
    images_for_frontend = [
        schemas.ImageInfo(url=img["url"], index=i)
        for i, img in enumerate(ALL_IMAGES_DATA)
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

    # 백엔드에 있는 ALL_IMAGES_DATA를 기반으로 해당 카테고리의 정답 인덱스를 찾습니다.
    correct_indices_for_category = {
        i for i, img in enumerate(ALL_IMAGES_DATA)
        if img["label"] == category_asked
    }

    # 사용자의 선택과 실제 정답을 비교
    is_correct = (selected_indices_set == correct_indices_for_category)

    # 결과 저장 (selected_indices는 사용자가 선택한 원본 인덱스를 그대로 저장)
    crud.save_result(db, payload.selected, is_correct)

    return schemas.ResultOut(is_correct=is_correct)

# 기존 /images 엔드포인트는 이제 사용하지 않거나, /question으로 대체될 것입니다.
# @router.get("/images", response_model=list[schemas.ImageInfo])
# def get_images():
#     # 이 엔드포인트는 더 이상 사용되지 않거나, 다른 목적으로 사용될 수 있습니다.
#     # 이제 /question 엔드포인트가 이미지 목록을 제공합니다.
#     pass