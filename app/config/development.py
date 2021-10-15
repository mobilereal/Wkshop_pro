config = {  #!การกำหนดการเชื่อมต่อเข้าสู่ Robo mongo
    "mongo_config": {
        "host": "localhost",
        "port": 27017,
        "user": "root",
        "password": "root",
        "auth_db": "admin",  # **ผู้ที่สามารถเข้าใช้dbได้ = admin
        "db": "bakerypj",  # **Database ขื่อ bakerypj
        "collection": "bakery",  # **ตารางที่ใช้ในการเก้บข้อมูลชื่อตาราง bakery
    }
}
