from fastapi import APIRouter,Depends, HTTPException, status, Query

from sqlalchemy import select, update, func, delete
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.order import OrderSchema, OrderItemSchema, OrderListSchema
from app.models import OrderItemModel, OrderModel, ProductModel,CartModel, UserModel
from app.validation.config import jwtmanager
from app.utilits import _get_order_item
from app.db_depends import get_async_db

from decimal import Decimal


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def new_order(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(jwtmanager.get_current_user)) -> OrderSchema:
    request_cart = await db.scalars(
        select(CartModel)
        .join(CartModel.product)
        .where(CartModel.user_id == current_user.id)
        .where(ProductModel.is_active == True)
        .where(ProductModel.price.isnot(None))
        .options(contains_eager(CartModel.product))         
    )
    carts = request_cart.all()
    if carts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина пуста!")
    
    order = OrderModel(user_id = current_user.id)
    total_amount = Decimal("0") #общая цена всех заказов

    for item in carts:
        if item.product.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Недостаточно количество товара на складе {item.product.name}")
        
        total_price_cart = item.quantity * item.product.price
        total_amount += total_price_cart
        order_item = OrderItemModel(
            product_id=item.product.id,#продукт айди
            quantity=item.quantity,#количество
            unit_price_product=item.product.price, #стоимость 1 товара
            total_price_cart=total_price_cart #стоимость количества товара в 1 заказе
        )
        item.product.stock -= item.quantity #уменьши количество продукта после покупки

        order.items.append(order_item) #добавляем в ордер обьект в связь автоматом создаться обьект order_item с остальными данными

    order.total_amount = total_amount
    db.add(order)
    await db.execute(delete(CartModel).where(CartModel.user_id == current_user.id))
    await db.commit()
    await db.refresh(order)

    created_order = await _get_order_item(db, order.id)
    if not created_order:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load created order",
        )
    return created_order

@router.get("/", response_model=OrderListSchema)
async def get_all_orders(
    page : int = Query(1, ge=1, description="Страница заказов"),
    page_size : int = Query(10, ge=1, description="Количества заказов на странице"),
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
) -> OrderListSchema:
    
    request_order = await db.scalars(
        select(OrderModel)
        .where(OrderModel.user_id == current_user.id)
        .offset((page-1) * page_size)
        .limit(page_size)
        .order_by(OrderModel.createt_at.desc())
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product)
        )
    )
    orders = request_order.all()
    total = await db.scalar(select(OrderModel.id).where(OrderModel.user_id == current_user.id))
    return {
        "items" : orders,
        "total" : total,
        "page" : page,
        "page_size" : page_size
    }
         
@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id : int,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
) -> OrderSchema:
    order = await _get_order_item(db, order_id)
    if not order  or  order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Доступ запрещен")
    return order
         
    