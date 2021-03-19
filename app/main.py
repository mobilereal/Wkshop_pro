#!import เพื่อใช้ฟังก์ชั่นต่างๆของAPI
import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

#!import เพื่อเชื่อมต่อกับดาต้าเบสMongoDB
from database.mongodb import MongoDB
from config.development import config
from model.bakery import (
    createBakeryModel,
    updateBakeryModel,
)  #! importฟังก์ชัน Create และ Update เข้าตัวตารางbakery

mongo_config = config["mongo_config"]
print("Mongo_config", mongo_config)


# ?  {
# ?         "host": "localhost",
# ?         "port": 27017,
# ?         "user": "root",
# ?         "password": "root",
# ?         "auth_db": "admin",
# ?         "db": "bakerypj",
# ?         "collection": "bakery",
# ? }


mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()  #!เชื่อมต่อกับDBแล้ว

app = FastAPI()  #!ทำการใช้API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: CRUD = Create:post , Read:get byid,all , Update:push,patch , Delete
# *******************************************************************************************************
@app.get(
    "/"
)  #!อ่านข้อมูลในdb แล้วreturnออกมาหากสามารถหาเจอได้ status code 200 คือ ปกติ
def index():
    return JSONResponse(content={"message": "Bakery Info"}, status_code=200)


# *******************************************************************************************************
@app.get(
    "/bakerys"
)  #!อ่านข้อมูลในdb มีการsortโดยเรียงmenu_typeตามตัวอักษร A-Z (ASD), Z-A (DSC)
def get_bakerys(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(
            order, sort_by
        )  # TODO: sort menu_type : A-Z (ASD), Z-A (DSC)
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  #!returnออกมาหากไม่สามารถหาเจอ status code 500 ให้แสดงใน terminal ว่า  Something went wrong !!

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,  #!returnออกมาหากสามารถหาเจอได้ status code 200 ให้แสดงใน terminal คือ ปกติ
    )


# *******************************************************************************************************


@app.get("/bakerys/{bakerys_id}")  #!pathเพื่อส่งพารามิเตอร์bakerys_id เพื่อหาข้อมูล
def get_bakerys_by_id(
    bakerys_id: str = Path(None, min_length=10, max_length=10)
):  #!ใส่IDอะไรก็ได้ไม่เกิน 10และไม่ต่ำกว่า10
    try:
        result = mongo_db.find_one(
            bakerys_id
        )  #!find_oneอันเดียว คือส่ง bakerys_id ที่ส่งมา (ควรมีไอดีเพียงอันเดียว)
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  #!500 API Error

    if result is None:
        raise HTTPException(
            status_code=404, detail="Bakery Id not found !!"
        )  #!404 คนคีย์IDผิด

    return JSONResponse(
        content={
            "status": "OK",
            "data": result,
        },  #!returnออกมาหากสามารถหาเจอได้ status code 200 ให้แสดงใน terminal คือ ปกติ
        status_code=200,
    )


# *******************************************************************************************************
@app.post("/bakerys")  #!ส่งMethod post เพื่อสร้างข้อมูลลงในdb
def create_books(bakery: createBakeryModel):
    try:
        bakery_id = mongo_db.create(bakery)  #!สร้างbakery_id ในตาราง bakery
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  #!500 API Error

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": bakery_id,
            },
        },
        status_code=201,  #!หากสามารถสร้างข้อมูลได้ status code 201 จะแสดงใน terminal คือ ปกติ
    )


# *******************************************************************************************************

#!อัพเดทบางฟีลแค่นั้น ใช้ patch


@app.patch(
    "/bakerys/{bakery_id}"
)  #!อัพเดทบางส่วนโดยส่งพารามิเตอร์ bakery_id เพื่อทำการอัพเดท
def update_books(
    bakery: updateBakeryModel,
    bakery_id: str = Path(
        None, min_length=10, max_length=10
    ),  #!ใส่IDอะไรก็ได้ไม่เกิน 10และไม่ต่ำกว่า10
):
    print("bakery", bakery)  #!ปริ้นค่า
    try:
        updated_bakery_id, modified_count = mongo_db.update(bakery_id, bakery)
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  #!500 API Error

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Bakery Id: {updated_bakery_id} is not update want fields",  #!404 คนคีย์IDผิด
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": updated_bakery_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,  #!หากทำงานได้ปกติจะแสดง เช่น {
        #!"status": "ok",
        #!"data": {
        #!    "bakery_id": "เลขไอดีที่อัพเดท",
        #!    "modified_count": 1
        #!}
    )


# *******************************************************************************************************


@app.delete("/bakerys/{bakery_id}")  #! ลบข้อมูลโดยระบุID
def delete_book_by_id(
    bakery_id: str = Path(None, min_length=10, max_length=10)
):  #!ใส่IDอะไรก็ได้ไม่เกิน 10และไม่ต่ำกว่า10
    try:
        deleted_bakery_id, deleted_count = mongo_db.delete(bakery_id)
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  #!500 API Error

    if deleted_count == 0:  # ถ้าลบdelcount = 0 เอาไอดีมาผิดจะบอกว่าไม่มีนะจีะ
        raise HTTPException(
            status_code=404,
            detail=f"Bakery Id: {deleted_bakery_id} is not Delete",  #!404 คนคีย์IDผิด
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": deleted_bakery_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,  #!หากสามารถลบข้อมูลได้ status code 200 จะแสดงใน terminal คือ ปกติ
    )


if __name__ == "__main__":  #! เชื่อม db ใข้ host="127.0.0.1" port=3001
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
