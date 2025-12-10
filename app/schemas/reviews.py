from pydantic import BaseModel, Field, ConfigDict, PositiveInt

from typing import Optional

from datetime import datetime

class ReviewCreate(BaseModel):
    product_id : PositiveInt
    comment : Optional[str] = Field(None, description="Комментарий пользователя")
    grade : int = Field(..., ge=1, le=5, description = "Введите оценку отзыва от 1 до 5")

    model_config = ConfigDict(from_attributes = True)


class Review(BaseModel):
    id : PositiveInt
    user_id : PositiveInt
    product_id : PositiveInt
    comment : Optional[str]
    comment_date : datetime
    grade : int
    is_active : bool

    model_config = ConfigDict(from_attributes = True)



