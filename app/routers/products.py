from fastapi import APIRouter, Depends, HTTPException,status

from app.shemas.products import ProductCreate, Product
from app.models import CategoryModel, ProductModel, UserModel
from app.database import select, update,AsyncSession
from app.validation.role_depends import can_manage
from app.db_depends import get_async_db




router = APIRouter(
    prefix = "/products",
    tags = ["products"]
)


@router.get("/", response_model = list[Product])
async def get_active_products(db : AsyncSession = Depends(get_async_db)) -> list[Product]:
    request_products = await db.scalars(
        select(ProductModel)
        .join(ProductModel.category)
        .where(ProductModel.is_active == True)
        .where(CategoryModel.is_active == True)
        .order_by(ProductModel.id.asc())
    )
    active_products = request_products.all()
    return active_products
 
    
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


@router.get("/products/{category_id}", response_model = list[Product])
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