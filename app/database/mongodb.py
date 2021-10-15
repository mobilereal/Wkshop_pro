import pymongo  #! import ฟังก์ชันให้สามารถใช้db mongoได้
from model.bakery import (
    createBakeryModel,
    updateBakeryModel,
)  #! importฟังก์ชัน Create และ Update เข้าตัวตารางbakery


class MongoDB:  #!คลาส MongoDB
    def __init__(
        self, host, port, user, password, auth_db, db, collection
    ):  #!การสร้างฟังก์ชัน contructure เพื่อเตรียมพร้อมตัวแปรก่อนจะนำค่าเข้ามา
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auth_db = auth_db
        self.db = db
        self.collection = collection
        self.connection = None

    # *******************************************************************************************************

    def _connect(self):  #! ฟังก์ชันการConnect กับMongodb
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            authSource=self.auth_db,
            authMechanism="SCRAM-SHA-1",  #!โปรโตคอลเพื่อทำการยืนยันก่อนทำการConnect กับ MongoDb
        )
        db = client[self.db]  #!เชื่อมตัวdb instant
        self.connection = db[self.collection]  #!สร้างcollection

    # *******************************************************************************************************

    def find(
        self, order, sort_by
    ):  #!ฟังก์ชั่นในการค้นหาทั้งหมด และจะแสดงการเรียง โดยเรียงmenu_typeตามตัวอักษร A-Z (ASD), Z-A (DSC)
        mongo_results = self.connection.find({})
        if sort_by is not None and order is not None:
            mongo_results.sort(sort_by, self._get_sort_by(order))

        return list(mongo_results)  #!Return ข้อมูลออกมาเป็นList

    # *******************************************************************************************************

    def _get_sort_by(
        self, sort: str
    ) -> int:  #! เลือกsort Z-A หรือ A-Z (น้อย->มาก หรือ มาก->น้อย)
        return pymongo.DESCENDING if sort == "desc" else pymongo.ASCENDING

    # *******************************************************************************************************

    def find_one(self, id):
        return self.connection.find_one(
            {"_id": id}
        )  #!หาเพียง 1 ตัวโดยใช้ID วึ่งไม่ต้องผ่านการsortใดๆ

    # *******************************************************************************************************

    def create(self, bakery: createBakeryModel):
        bakery_dict = bakery.dict(
            exclude_unset=True
        )  # *สร้างแล้วรับมาเแปลงเป็นdictเก็บไว้
        #!1. ADDRESSเดิม
        insert_dict = {**bakery_dict, "_id": bakery_dict["id"]}

        inserted_result = self.connection.insert_one(insert_dict)
        bakery_id = str(inserted_result.inserted_id)
        #!2.  **เวลาสร้างจะเป็นaddใหม่เสมอ
        return bakery_id  #!ส่งค่าไปโชว์เป็นเลขไอดีที่สร้าง

    # *******************************************************************************************************

    def update(self, bakery_id, bakery: updateBakeryModel):  #!อัพเดทข้อมูล
        updated_result = self.connection.update_one(
            {"id": bakery_id},
            {
                "$set": bakery.dict(exclude_unset=True)
            },  #!กำหนดID แล้วอัพเดทในส่วนข้อbodyเพียง1ฟีลได้หรือจะอัพเดททั้งหมด ก็พิมเอาให้ครบตามใจเลยจ้า
        )
        return [
            bakery_id,
            updated_result.modified_count,
        ]  #!โชว์ไอดีที่อพีเดท แล้วจำนวนที่ได้อัพเดทไปกี่ตัว

    # *******************************************************************************************************

    def delete(self, bakery_id):  #! ลบก็คือลบ
        deleted_result = self.connection.delete_one(
            {"id": bakery_id}
        )  #!ลบโดยกำหนดID ของdata setนั้นๆได้
        return [
            bakery_id,
            deleted_result.deleted_count,
        ]  #!โชว์ว่าลบIDไหนไป แล้วมีจำนวนกี่ตัวที๋โดนลบ
