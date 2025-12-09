from pydantic import BaseModel, PositiveInt, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Введите название товара (3-20 символов)")
    description: Optional[str] = Field(None, max_length=500, description="Введите описание до 500 символов")
    price: Decimal = Field(..., gt=0, description="Введите цену больше 0", examples=[99.99])
    image_url: Optional[str] = Field(None, max_length=200, description="URL изображения до 200 симоволов")
    stock: int = Field(..., gt=0, description="Количество товара, больше 0")
    category_id: PositiveInt = Field(..., description="ID категории к которой принадлежит товар")

    
    

class Product(BaseModel):
    id: PositiveInt = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., min_length=3, max_length=40, description="Введите название товара (3-20 символов)")
    description: Optional[str] = Field(None, max_length=500, description="Введите описание до 500 символов")
    price: Decimal = Field(..., gt=0, description="Введите цену больше 0",examples=[99.99])
    image_url: Optional[str] = Field(None, max_length=200, description="URL изображения до 200 симоволов")
    stock: int = Field(..., gt=0, description="Количество товара, больше 0")
    category_id: PositiveInt = Field(..., description="ID категории к которой принадлежит товар")
    seller_id : PositiveInt = Field(..., description="Айди продавца")
    is_active: bool = Field(..., description="Активность товара")

    model_config = ConfigDict(from_attributes=True)
    


class ProductCount(BaseModel):
    count_product : int = Field(..., description = "Количество товара")

class ProductPopularity(BaseModel):
    product : Product
    category_name : str = Field(..., description = "Категория товара")

    model_config = ConfigDict(from_attributes = True)