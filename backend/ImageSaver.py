"""
import os
import uuid
import sqlalchemy
from app import database, models

file_path = input("파일 경로: ")
src_name = input("출처 이름: ")


db = database.SessionLocal()
for i in os.listdir(file_path):
    if os.path.isdir(os.path.join(file_path, i)):
        for j in os.listdir(j):
            u = uuid.uuid4()
            os.rename(os.path.join(file_path, i, j), os.path.join(file_path, ))
            db.add(models.ImagePath(
                uuid = u,
                path = r,
                label = i,
                source = src_name
            ))
            db.commit()
db.close()            
"""

