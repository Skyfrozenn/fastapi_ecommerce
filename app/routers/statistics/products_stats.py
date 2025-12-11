from fastapi import APIRouter, Depends

from app.database import select, func, Session,desc, AsyncSession,joinedload
from app.models import ProductModel, CategoryModel, ReviewModel, UserModel
from app.schemas.products import  ProductCount, ProductPopularity
from app.db_depends import get_db, get_async_db
from app.validation.role_depends import get_admin_user



router = APIRouter(
    prefix="/statistics/products",  
    tags=["Statistics - Products"]
)


@router.get("/active", response_model=ProductCount)
async def get_count_active_products(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)) -> str:
    request_product = await db.scalars(select(func.count(ProductModel.id)).where(ProductModel.is_active == True))
    result = request_product.first()
    return  {"count_product" : result}


@router.get("/inactive",response_model=ProductCount)
async def get_count_inactive_products(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_product = await db.scalars(select(func.count(ProductModel.id)).where(ProductModel.is_active == False))
    result = request_product.first()
    return  {"count_product" : result}
     


@router.get("/total", response_model=ProductCount)
async def get_total_count_products(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_product = await db.scalars(select(func.count(ProductModel.id)))
    result = request_product.first()
    return  {"count_product" : result}


@router.get("/most-expensive", response_model = ProductPopularity)
async def get_most_expensive_product(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)) -> ProductPopularity:
    request_product = await db.scalars(
        select(ProductModel)
        .join(ProductModel.category)
        .where(ProductModel.is_active == True)
        .where(CategoryModel.is_active == True)
        .order_by(ProductModel.price.desc())
        .options(joinedload(ProductModel.category))
    )
    result = request_product.first()
    return {
        "product" : result,
        "category_name" : result.category.name
    }
         




@router.get("/most-cheapest", response_model = ProductPopularity)
async def get_cheapest_product(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)) -> ProductPopularity:
    request_product = await db.scalars(
        select(ProductModel)
        .join(ProductModel.category)
        .where(ProductModel.is_active == True)
        .where(CategoryModel.is_active == True)
        .order_by(ProductModel.price.asc())
        .options(joinedload(ProductModel.category))
    )
    result = request_product.first()
    return {
        "product" : result,
        "category_name" : result.category.name
    }
    

@router.get("/most-reviews")
async def get_most_popular_products(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_product = await db.execute(
        select(
            ProductModel,
            func.count(ReviewModel.id)            
        )
        .join(ProductModel.reviews)
        .where(ReviewModel.is_active == True)
        .group_by(ProductModel.id)
        .order_by(func.count(ReviewModel.id).desc())
        .limit(1)
    )
    result = request_product.first()
     
    if result is not None:
        product, count_reviews = result
        return {
        "product" : product,
        "count_reviews" : count_reviews
        }
    else:
        return {"message" : "Товаров с отзывами еще нет"}


@router.get("/fewer-reviews")
async def get_most_popular_products(db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_product = await db.execute(
        select(
            ProductModel,
            func.count(ReviewModel.id)            
        )
        .join(ProductModel.reviews)
        .where(ReviewModel.is_active == True)
        .group_by(ProductModel.id)
        .order_by(func.count(ReviewModel.id).asc())
        .limit(1)
    )
    result = request_product.first()
     
    if result is not None:
        product, count_reviews = result
        return {
        "product" : product,
        "count_reviews" : count_reviews
        }
    else:
        return {"message" : "Товаров с отзывами еще нет"}

 