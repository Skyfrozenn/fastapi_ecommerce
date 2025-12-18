from pydantic import Field, BaseModel, PositiveInt, ConfigDict
from decimal import Decimal
from app.schemas.products import Product

class CartItemBase(BaseModel):
    product_id : int = Field(..., description="Айди товара")
    quantity : int = Field(..., ge=1, description="Количества товара больше или равно одному")



class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину"""
    pass


class CartItemUpdate(BaseModel):
    quantity : int = Field(..., ge=1, description="Количества товара больше или равно одному")


class CartItemResponce(BaseModel):
    id : PositiveInt =  Field(..., description="ID товара в корзине")
    quantity : int = Field(..., ge=1, description="Количества товара больше или равно одному")
    product : Product = Field(..., description="Описание товара")
    

    model_config = ConfigDict(from_attributes=True)


class CartUser(BaseModel):
    user_id : PositiveInt = Field(..., description="Id юзера,которому принадлежит товар")
    items : list[CartItemResponce] = Field(..., description="Описание товара в корзине")
    total_quantity : int = Field(..., description="Общее количество товаров в корзине")
    total_price : Decimal = Field(..., examples=["99.99"], description="Общая стоимость корзины")

    model_config = ConfigDict(from_attributes=True)

