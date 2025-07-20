from pydantic import BaseModel
from typing import List, Dict, Union

class ImageInfo(BaseModel):
    uuid: str
    url: str
    index: int # 프론트엔드에서 이미지의 인덱스를 쉽게 관리하기 위해 추가

class QuestionInfo(BaseModel):
    category: str # 사용자가 맞춰야 할 카테고리 (예: "cardboard")
    images: List[ImageInfo] # 현재 질문에 사용될 이미지 목록

class ResultIn(BaseModel):
    images: List[ImageInfo]
    selected: List[str]
    category_asked: str # 사용자가 어떤 카테고리에 대해 답변했는지 백엔드에 전달

class ResultOut(BaseModel):
    is_correct: bool
    # 필요하다면 추가 정보 (예: 올바른 선택이었는지 등)