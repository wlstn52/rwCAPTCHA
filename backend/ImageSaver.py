import os
import uuid
import sqlalchemy
from app import database, models

file_path = input("파일 경로: ")
src_name = input("출처 이름: ")


db = database.SessionLocal()
for i in os.listdir(file_path):
    if os.path.isdir(os.path.join(file_path, i)):
        for j in os.listdir(os.path.join(file_path, i)):
            u = uuid.uuid4()
            os.rename(os.path.join(file_path, i, j), f"C:\\Users\\jskim\\OneDrive\\Desktop\\HSC\\rwCAPTCHA\\backend\\img\\{u}.jpg")
            db.add(models.ImagePath(
                uuid = u,
                path = f"/img/{u}.jpg",
                label = i,
                source = src_name
            ))
            db.commit()
db.close()            


