from fastapi import APIRouter, Depends

from app.database import select, Session, desc, func, AsyncSession
from app.models import CategoryModel, ProductModel
from app.schemas.categories import CategoryStats, CategoryPopularity, CategoryCount
from app.db_depends import get_db, get_async_db

router = APIRouter(
    prefix="/statistics/categories",
    tags=["Statistics -> Categories"]
)

@router.get("/active", response_model = CategoryCount)
async def get_count_active_categories(db : AsyncSession = Depends(get_async_db)) -> str:
    result = await db.scalars(select(func.count(CategoryModel.id)).where(CategoryModel.is_active == True))
    count = result.first()
    return  {"category_count" : count}


@router.get("/inactive", response_model=CategoryCount)
async def get_count_inactive_categories(db : AsyncSession = Depends(get_async_db)) -> str:
    result = await db.scalars(select(func.count(CategoryModel.id)).where(CategoryModel.is_active == False))
    count = result.first()
    return  {"category_count" : count}

@router.get("/total", response_model=CategoryCount)
async def get_total_count_categories(db : AsyncSession = Depends(get_async_db)):
    result =  await db.scalars(select(func.count(CategoryModel.id)))
    count = result.first()
    return  {"category_count" : count}



@router.get("/most-expensive", response_model=CategoryStats) #самая дорогая
async def get_most_expensive_category(db : AsyncSession = Depends(get_async_db)):
    request_category = await db.execute(
        select(
            CategoryModel,
            func.max(ProductModel.price).label("max_price"),
            func.min(ProductModel.price).label("min_price"),
            func.avg(ProductModel.price).label("avg_price"),
            func.count(ProductModel.id).label("product_count")
        )
        .join(CategoryModel.products)
        .where(ProductModel.is_active == True)
        .group_by(CategoryModel.id)
        .order_by(desc(func.max(ProductModel.price))) #максимальная цена
        
    )
    result = request_category.first()
    category,max_price,min_price, avg_price,products_count = result
    return {
        "category" : category,
        "max_price" : max_price,
        "min_price" : min_price,
        "avg_price" : avg_price,
        "products_count" : products_count
    }
         

    


@router.get("/most-cheapest",response_model=CategoryStats) #самая дешевая
async def get_category_with_cheapest_product(db: AsyncSession = Depends(get_async_db)):
    request_category = await  db.execute(
        select(
            CategoryModel,
            func.max(ProductModel.price).label("max_price"),
            func.min(ProductModel.price).label('min_price'),
            func.avg(ProductModel.price).label('avg_price'),
            func.count(ProductModel.id).label('products_count')
        )
        .join(CategoryModel.products)
        .where(ProductModel.is_active == True)
        .group_by(CategoryModel.id)
        .order_by(func.min(ProductModel.price))  # самая низкая минимальная цена
        
    )
    result = request_category.first()
    
    if not result:
        return "Категорий пока что нет"
     
    category,max_price, min_price, avg_price, products_count = result
     
    
    return {
         
        "category": category,
        "max_price" : max_price,
        "min_price": min_price,
        "avg_price": avg_price,
        "products_count": products_count
    }


@router.get("/max-products", response_model=CategoryPopularity)
async def get_products_leader_category(db : AsyncSession = Depends(get_async_db)):
    request_category = await  db.execute(
        select(
            CategoryModel,
            func.count(ProductModel.id)
        )
        .join(CategoryModel.products)
        .where(ProductModel.is_active == True)
        .group_by(CategoryModel.id)
        .order_by(desc(func.count(ProductModel.id)))
        
                  
    )
     
    result = request_category.first()
    category, count_product = result

    return {
        "category" : category,
        "count_product" : count_product
    }



@router.get("/min-products", response_model=CategoryPopularity)
async def get_products_min_category(db : AsyncSession = Depends(get_async_db)):
    request_category = await db.execute(
        select(
            CategoryModel,
            func.count(ProductModel.id)
        )
        .join(CategoryModel.products)
        .where(ProductModel.is_active == True)
        .group_by(CategoryModel.id)
        .order_by(func.count(ProductModel.id))
        
                  
    )

    result = request_category.first()
    category, count_product = result

    return {
        "category" : category,
        "count_product" : count_product
    }



