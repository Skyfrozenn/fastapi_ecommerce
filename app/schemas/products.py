from pydantic import BaseModel, PositiveInt, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from fastapi import Form

from app.schemas.reviews import Review
from typing import Annotated, Optional


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Введите название товара (3-20 символов)")
    description: Optional[str] = Field(None, max_length=500, description="Введите описание до 500 символов")
    price: Decimal = Field(..., ge=0, description="Введите цену больше 0", examples=[99.99])
    stock: int = Field(..., gt=0, description="Количество товара, больше 0")
    category_id: PositiveInt = Field(..., description="ID категории к которой принадлежит товар")

    @classmethod
    def as_form(
        cls, 
        name: Annotated[str, Form(...)],           # обязательный
        price: Annotated[Decimal, Form(...)],      # обязательный
        stock : Annotated[int, Form(...)],        # обязательный
        category_id : Annotated[PositiveInt, Form(...)],  # обязательный
        description: Annotated[Optional[str], Form()] = None,  # с default
    ) -> "ProductCreate":
        return cls(
            name=name,
            price=price,
            stock=stock,
            category_id=category_id,
            description=description
        )
        
        

    
    

class Product(BaseModel):
    id: PositiveInt  
    name: str  
    description: Optional[str]  
    price: Decimal = Field(..., examples=["99.99"])
    image_url: str | None 
    stock: int  
    category_id: PositiveInt  
    seller_id : PositiveInt  
    rating : float  
    is_active: bool

    
     

    model_config = ConfigDict(from_attributes=True)

 

class ProductDetail(Product):  # Наследуем и добавляем отзывы
    reviews: list[Review]

class ProductCount(BaseModel):
    count_product : int = Field(..., description = "Количество товара")

class ProductPopularity(BaseModel):
    product : Product
    category_name : str = Field(..., description = "Категория товара")

    model_config = ConfigDict(from_attributes = True)

class ProductList(BaseModel):
    items : list[ProductDetail] = Field(description="Товары для текущей страницы")
    total : int = Field(ge=0, description="Общее количество товаров")
    page : int = Field(ge=1, description="Номер страницы")
    page_size : int = Field(description="Общее количество товаров")

    model_config = ConfigDict(from_attributes=True)