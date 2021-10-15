from typing import Optional, List
from pydantic import BaseModel, Field

# TODO: Insert ต้องใส่ให้ครบนะจ๊ะ
class createBakeryModel(BaseModel):
    id: str = Field(min_length=10, max_length=10)
    menu_name: str
    menu_type: str
    price: float
    piece: int
    picture_url: str


# TODO: อัพเดท (ถ้าเฉพาะฟิล ควรใช้patch ถ้าใช้pushต้องอัพเดททั้งก้อน)
class updateBakeryModel(BaseModel):
    menu_name: Optional[str]
    menu_type: Optional[str]
    price: Optional[float]
    piece: Optional[int]
    picture_url: Optional[str]
