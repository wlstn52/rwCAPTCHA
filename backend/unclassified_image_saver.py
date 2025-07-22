# unclassified_image_saver.py
import os
import uuid
import sqlalchemy
# app 모듈 경로에 맞게 조정해야 할 수 있습니다. (예: from your_project_name import database, models)
# 프로젝트 구조에 따라 상위 폴더를 참조해야 할 수도 있습니다.
# 예를 들어, backend 폴더가 프로젝트 루트라면 from backend import database, models 로 변경하거나,
# 스크립트를 backend 폴더 바깥에 두고 PYTHONPATH를 설정할 수 있습니다.
# 여기서는 app 이라는 가상의 루트 디렉토리 안에 database와 models가 있다고 가정합니다.
# 만약 ImageSaver.py가 작동했다면, 동일한 import 문을 사용하면 됩니다.
from app import database, models

file_path = input("미분류 이미지 파일 경로 (폴더 또는 단일 파일): ")
src_name = input("출처 이름 (선택 사항, 비워두려면 엔터): ")

db = database.SessionLocal()
try:
    if os.path.isdir(file_path):  # 폴더를 지정한 경우
        for j in os.listdir(file_path):
            full_image_path = os.path.join(file_path, j)
            if os.path.isfile(full_image_path):  # 파일인지 확인
                u = uuid.uuid4()
                # 이미지 저장 경로를 실제 프로젝트에 맞게 수정해주세요.
                # 예: 'C:\\Users\\USER\\OneDrive\\바탕 화면\\project\\rwCAPTCHA\\backend\\img\\'
                destination_dir = "C:\\Users\\USER\\OneDrive\\바탕 화면\\project\\rwCAPTCHA\\backend\\img\\"
                destination_path = os.path.join(destination_dir, f"{u}.jpg")

                # 파일 확장자 확인 (선택 사항, jpg/png 등으로 제한 가능)
                if not j.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    print(f"경고: {j}는 지원되지 않는 이미지 파일 형식이 아닙니다. 건너뜜니다.")
                    continue

                os.rename(full_image_path, destination_path)
                db.add(models.ImagePath(
                    uuid=u,
                    path=f"/img/{u}.jpg",
                    label="unclassified",  # 고정적으로 "unclassified" 라벨 사용
                    source=src_name if src_name else None  # 출처가 없으면 None
                ))
                db.commit()
                print(f"이미지 {j}를 미분류로 저장했습니다.")
    elif os.path.isfile(file_path):  # 단일 파일을 지정한 경우
        u = uuid.uuid4()
        destination_dir = "C:\\Users\\USER\\OneDrive\\바탕 화면\\project\\rwCAPTCHA\\backend\\img\\"
        destination_path = os.path.join(destination_dir, f"{u}.jpg")

        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            print(f"경고: {file_path}는 지원되지 않는 이미지 파일 형식이 아닙니다. 건너뜁니다.")
        else:
            os.rename(file_path, destination_path)
            db.add(models.ImagePath(
                uuid=u,
                path=f"/img/{u}.jpg",
                label="unclassified",
                source=src_name if src_name else None
            ))
            db.commit()
            print(f"이미지 {file_path}를 미분류로 저장했습니다.")
    else:
        print("유효하지 않은 파일 또는 폴더 경로입니다.")

except sqlalchemy.exc.IntegrityError as e:
    db.rollback()
    print(f"데이터베이스 오류 발생: {e}. 중복된 UUID일 수 있습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    db.close()