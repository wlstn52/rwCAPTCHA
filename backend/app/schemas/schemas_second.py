from pydantic import BaseModel
from typing import List, Dict, Union

class ImageInfo(BaseModel):
    uuid: str
    url: str
    index: int

class QuestionInfo(BaseModel):
    images: List[ImageInfo]

class ResultIn(BaseModel):
    images: List[ImageInfo]
    answers: List[str]

class ResultOut(BaseModel):
    is_correct: bool