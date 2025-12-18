from fastapi import HTTPException, status

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ReviewModel, ProductModel, CartModel

 

 

async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


async def _ensure_product_available(db : AsyncSession, product_id : int):
    request_product = await db.scalars(
        select(ProductModel)
        .where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = request_product.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден или не активен")


async def _get_cart_item(db : AsyncSession, user_id : int, product_id : int):
    request_cart = await db.scalars(
        select(CartModel)
        .where(CartModel.user_id == user_id, CartModel.product_id == product_id)
        .options(joinedload(CartModel.product))
    )
    cart = request_cart.first()
    return cart  