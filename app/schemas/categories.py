from pydantic import BaseModel, PositiveInt, Field,ConfigDict
from typing import Optional
 


class CategoryCreate(BaseModel):
    name : str =  Field(..., min_length=3, max_length=50, description="Введите название категории от 3 до 50 символов")
    parent_id : Optional[int] =  Field(default=None, description="ID родительской категории если есть")


class Category(BaseModel):
    id : PositiveInt =  Field(..., description="ID уникальный идентификатор категории")
    name : str = Field(..., min_length=3, max_length=50, description="Введите название категории от 3 до 50 символов")
    parent_id : Optional[int] =  Field(default=None, description="ID родительской категории если есть")
    is_active : bool =  Field(..., description="Активность категории")

    model_config = ConfigDict(from_attributes = True)


class CategoryStats(BaseModel):
    category: Category
    min_price: float 
    max_price: float 
    avg_price: float
    products_count: int

    model_config = ConfigDict(from_attributes=True)


class CategoryPopularity(BaseModel):
    category : Category
    count_product : int

    model_config = ConfigDict(from_attributes=True)

class CategoryCount(BaseModel):
    category_count : int = Field(..., description="Количества категорий")