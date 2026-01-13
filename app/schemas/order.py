from pydantic import BaseModel, Field, PositiveInt, ConfigDict
from decimal import Decimal

from app.schemas.products import Product
from datetime import datetime
from typing import Optional


class OrderItemSchema(BaseModel):
    id : PositiveInt = Field(..., description="Уникальный id продукта заказа")
    order_id : PositiveInt = Field(..., description="ID заказа")
    product_id : PositiveInt = Field(..., description="ID продукта в заказе")
    quantity : int = Field(..., ge=1, description="Количество продуктов в заказе")
    unit_price_product : Decimal = Field(..., ge=0, description="Цена за единицу товара в момент покупки", examples=["9999.99"])
    total_price_cart : Decimal = Field(..., ge=0, description="Общая цена продуктов в заказе", examples=["9999.99"])
    product : Product | None = Field(None,  description="Информация о товаре в заказе")

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    id : PositiveInt = Field(..., description="Уникальный ID заказа")
    user_id : PositiveInt = Field(..., description="ID юзера которому принадлежит заказ")
    status : str = Field(..., description="Статус заказа")
    total_amount : Decimal = Field(...,ge=0, description="Общая стоимость товара")
    createt_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    payment_id : Optional[str] = Field(None, max_length=64, description="Айди платежа с юкасса")
    paid_at : Optional[datetime] = Field(None, description="Дата создания платежа в Юкасса")
    items: list[OrderItemSchema] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


class OrderListSchema(BaseModel):
    items : list[OrderSchema] = Field(..., description="Описание заказов пользователей")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)



class OrderCheckoutResponse(BaseModel):
    order: OrderSchema = Field(..., description="Созданный заказ")
    confirmation_url: str | None = Field(
        None,
        description="URL для перехода на оплату в YooKassa",
    )