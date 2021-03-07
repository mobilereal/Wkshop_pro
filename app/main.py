import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.bakery import createBakeryModel, updateBakeryModel

mongo_config = config["mongo_config"]
print("Mongo_config", mongo_config)


#  {
#         "host": "localhost",
#         "port": 27017,
#         "user": "root",
#         "password": "root",
#         "auth_db": "admin",
#         "db": "bakerypj",
#         "collection": "bakery",
# }


mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect() #เชื่อมละ

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#CRUD = create:post ,Read:get byid,all , update:push,patch , del
@app.get("/")
def index():
    return JSONResponse(content={"message": "Bakery Info"}, status_code=200)


@app.get("/bakerys/") 
def get_bakerys(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/bakerys/{bakerys_id}")#pathพารามิเตอร์student_id
def get_bakerys_by_id(bakerys_id: str = Path(None, min_length=10, max_length=10)):#ใส่ไรก็ได้ไม่เกิน 10 
    try:
        result = mongo_db.find_one(bakerys_id) #findoneอันเดียว คือstd id ที่ส่งมา ควรมีไอดีเพียงอันเดียว
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!") #500 API Error

    if result is None:
        raise HTTPException(status_code=404, detail="Bakery Id not found !!") #404 คนคีย์ผิด

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/bakerys")
def create_books(bakery: createBakeryModel):
    try:
        bakery_id = mongo_db.create(bakery)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": bakery_id,
            },
        },
        status_code=201,
    )

#อัพเดทบางฟีลแค่นั้น ใช้patch
@app.patch("/bakerys/{bakery_id}")
def update_books(
    bakery: updateBakeryModel,
    bakery_id: str = Path(None, min_length=10, max_length=10),#ไม่มากไม่น้อยกว่า10
):
    print("bakery", bakery)
    try:
        updated_bakery_id, modified_count = mongo_db.update(bakery_id, bakery)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Bakery Id: {updated_bakery_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": updated_bakery_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/bakerys/{bakery_id}")
def delete_book_by_id(bakery_id: str = Path(None, min_length=10, max_length=10)):
    try:
        deleted_bakery_id, deleted_count = mongo_db.delete(bakery_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0: #ถ้าลบdelcount = 0 เอาไอดีมาผิดจะบอกว่าไม่มีนะจีะ
        raise HTTPException(
            status_code=404, detail=f"Bakery Id: {deleted_bakery_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "bakery_id": deleted_bakery_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
