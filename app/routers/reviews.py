from fastapi import APIRouter, HTTPException, status, Depends


from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reviews import Review, ReviewCreate
from app.models import ReviewModel, UserModel, ProductModel
from app.db_depends import get_async_db
from app.validation import jwtmanager
from app.utilits import update_product_rating


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

@router.get("/", response_model=list[Review])
async def get_all_reviews(db : AsyncSession = Depends(get_async_db)):
    request_reviews = await db.scalars(
        select(ReviewModel)
        .where(ReviewModel.is_active == True)
    )
    reviews = request_reviews.all()
    return reviews

@router.get("/{review_id}", response_model=Review)
async def get_info_review(review_id : int, db : AsyncSession = Depends(get_async_db)):
    request_review = await db.execute(
        select(ReviewModel)
        .where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    )
    review = request_review.scalar()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не активен или не существует")
     
    return review


@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def new_review(
    review_create : ReviewCreate,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user) 
) -> Review:
    request_product = await db.execute(
        select(ProductModel)
        .where(ProductModel.id == review_create.product_id, ProductModel.is_active == True)
    )
    product = request_product.scalar()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не активен или не существует")
    reviews = ReviewModel(**review_create.model_dump(), user_id = current_user.id)
    db.add(reviews)
    await db.commit()
    await db.refresh(reviews)

    await update_product_rating(db, reviews.product_id)

    return reviews


@router.put("/{review_id}", response_model=Review)
async def update_review(
    review_id : int,
    new_review : ReviewCreate,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
) -> UserModel:
    request_review = await db.execute(
        select(ReviewModel)
        .where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    )
    review = request_review.scalar()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не активен или не существует")

    if current_user.role != "admin":
        if review.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только создатель  или админ может изменять отзывы")
    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(**new_review.model_dump(), user_id = current_user.id))
    await db.commit()
    await db.refresh(review)
    await update_product_rating(db, review.product_id)
    return review


@router.delete("/{review_id}")
async def delete_review(
    review_id : int,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(jwtmanager.get_current_user)
) -> dict:
    request_review = await db.execute(
        select(ReviewModel)
        .where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    )
    review = request_review.scalar()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не активен или не существует")
     
    if current_user.role != "admin":
        if review.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только создатель  или админ может удалять отзывы")
    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(is_active = False))
    await db.commit()
    await db.refresh(review)

    await update_product_rating(db, review.product_id)
    return {"status": "success", "message": "Review marked as inactive"}
                     
    
    
    
