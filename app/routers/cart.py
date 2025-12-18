from fastapi import APIRouter, Depends, status, HTTPException, Response

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cart import CartItemCreate, CartItemResponce, CartItemUpdate, CartUser
from app.models import ProductModel, CartModel, UserModel
from app.db_depends import get_async_db
from app.validation.config import jwtmanager
from app.utilits import _ensure_product_available, _get_cart_item

from decimal import Decimal



router = APIRouter(
    prefix="/cart",
    tags=["Cart"] 
)


@router.get("/", response_model=CartUser)
async def get_cart(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(jwtmanager.get_current_user)) -> CartUser:
    request_cart = await db.scalars(
        select(CartModel)
        .where(CartModel.user_id == current_user.id)
        .order_by(CartModel.created_at.desc())
        .options(selectinload(CartModel.product))
    )
    cart = request_cart.all()
    total_quantity = sum(item.quantity for item in cart)
    price_items = (
        Decimal(item.quantity) * 
        (item.product.price if item.product.price is not None else Decimal("0"))
        for item in cart
    )
    total_price_decimal = sum(price_items, Decimal("0"))
    return {
        "user_id" : current_user.id,
        "items" : cart,
        "total_quantity" : total_quantity,
        "total_price" : total_price_decimal
    }


@router.post("/items", response_model=CartItemResponce, status_code=status.HTTP_201_CREATED)
async def add_product_cart(
    cart_create : CartItemCreate,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
) -> CartItemResponce:
    await _ensure_product_available(db, product_id=cart_create.product_id)
    cart_item = await _get_cart_item(db, user_id=current_user.id, product_id=cart_create.product_id)
    if cart_item:
        cart_item.quantity += cart_create.quantity
    else:
        cart_obj = CartModel(**cart_create.model_dump(), user_id = current_user.id)
        db.add(cart_obj)
        await db.commit()
    updated_item = await _get_cart_item(db, user_id=current_user.id, product_id=cart_create.product_id)
    return updated_item


@router.put("/items/{product_id}")
async def update_cart_item(
    product_id : int,
    payload : CartItemUpdate,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
):
    await _ensure_product_available(db=db, product_id=product_id)

    product = await _get_cart_item(db=db, user_id=current_user.id, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар в корзине не найден")
    product.quantity = payload.quantity
    await db.commit()
    update_product = await _get_cart_item(db=db, user_id=current_user.id, product_id=product_id)
    return update_product

@router.delete("items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def rewove_item_for_cart(
    product_id : int ,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
):
    await _ensure_product_available(db=db, product_id=product_id)
    item_cart = await _get_cart_item(db=db, user_id=current_user.id, product_id=product_id)
    if item_cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар в корзине не найден")
    await db.delete(item_cart)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
):
    await db.execute(delete(CartModel).where(CartModel.user_id == current_user.id))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    

    
    
