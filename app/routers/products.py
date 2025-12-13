from fastapi import APIRouter, Depends, HTTPException,status, Query

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.products import ProductCreate, Product, ProductDetail, ProductList
from app.models import CategoryModel, ProductModel, UserModel, ReviewModel
 
from app.validation.role_depends import can_manage
from app.db_depends import get_async_db




router = APIRouter(
    prefix = "/products",
    tags = ["products"]
)


    #items : list[ProductDetail] = Field(description="Товары для текущей страницы")
    #total : int = Field(ge=0, description="Общее количество товаров")
    #page : int = Field(ge=1, description="Номер страницы")
    #page_size
 


@router.get("/", response_model = ProductList)
async def get_active_products(
    page : int = Query(1, ge=1),
    page_size : int = Query(5, ge=1),
    category_id : int | None = Query(None, description="Категория для товаров"),
    min_price : float | None = Query(None, ge=0, description="Минимальная цена" ),
    max_price : float | None = Query(None, ge=0, description="Максимальная цена"),
    seller_id : int | None = Query(None, ge=0, description="ID продавца или фильтрация"),
    is_active : bool | None = Query(None, description="True актианые товары / False товары не в наличии"),
    db : AsyncSession = Depends(get_async_db)
) -> ProductList:
    
    product_total_request = await db.execute(select(func.count(ProductModel.id)).where(ProductModel.is_active == True))
    total = product_total_request.scalar()

    filters = [ProductModel.is_active == True]
    if category_id is not None:
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= max_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)
    if is_active is not None:
        filters.append(ProductModel.is_active == is_active)

    
    products = await db.scalars(
        select(ProductModel)
        .join(ProductModel.category)
        .where(*filters)
        .where(CategoryModel.is_active == True)
        .offset((page - 1) * page_size)
        .options(
            selectinload(ProductModel.reviews.and_(ReviewModel.is_active == True))
        )
        .order_by(ProductModel.id.asc())
        .limit(page_size)
    )
    return {
        "items" : products.all(),
        "total" : total,
        "page" : page,
        "page_size" : page_size

    }
     
 
    
@router.post("/", response_model = Product, status_code=status.HTTP_201_CREATED)
async def new_product(new_product : ProductCreate, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(can_manage) ) -> Product:
    request_category = await db.scalars(select(CategoryModel).where(CategoryModel.id == new_product.category_id, CategoryModel.is_active == True))
    category = request_category.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Указанная категория товара не найдена")
    
    product_data = new_product.model_dump()
    product_data["seller_id"] = current_user.id
    product = ProductModel(**product_data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/products/{category_id}", response_model = list[ProductDetail])
async def active_products_category(category_id : int, db : AsyncSession = Depends(get_async_db)):
    request_category = await db.scalars(select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True))
    category = request_category.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Категория не активна или не существует")
    request_product = await db.scalars(select(ProductModel).where(ProductModel.category_id == category.id, ProductModel.is_active == True))
    products = request_product.all()
    return products

@router.get("/{product_id}", response_model = Product)
async def get_product(product_id : int, db : AsyncSession = Depends(get_async_db)) -> Product:
    request_product = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = request_product.first()
    return product


@router.put("/{product_id}", response_model = Product)
async def update_product(product_id : int, new_product : ProductCreate, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(can_manage)) -> Product:
    request_product = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = request_product.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Товар не найден или не активен")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Только продавец может изменять свои товары!")
    request_category = await db.scalars(select(CategoryModel).where(CategoryModel.id == new_product.category_id, CategoryModel.is_active == True))
    category = request_category.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Указаная категория не найдена или не активна")
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**new_product.model_dump()))
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", response_model = Product)
async def deactivation_status_product(product_id : int, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(can_manage)) -> Product:
    request_product = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = request_product.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Товар не найден")
    if current_user.role == "seller":
        if product.seller_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только админ или владец товара может его удалить!")
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active = False))
    await db.commit()
    await db.refresh(product)
    return product