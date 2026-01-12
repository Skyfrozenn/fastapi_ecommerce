from fastapi import APIRouter, Depends, HTTPException,status, Query, UploadFile, File, Form

from sqlalchemy import select, update, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pathlib import Path
import uuid


from app.schemas.products import ProductCreate, Product, ProductDetail, ProductList
from app.models import CategoryModel, ProductModel, UserModel, ReviewModel

from app.validation.role_depends import can_manage
from app.db_depends import get_async_db



BASE_DIR = Path(__file__).resolve().parent.parent.parent 
MEDIA_ROOT = BASE_DIR / "media" / "products" 
MEDIA_ROOT.mkdir(parents=True, exist_ok=True) 
ALLOWED_IMAGES_TYPES = ["image/jpeg", "image/png", "image/gif"]
MAX_IMAGE_SIZE = 2 * 1024 * 1024 #2мб



router = APIRouter(
    prefix = "/products",
    tags = ["products"]
)


async def save_image(file : UploadFile) -> str:
    """Сохраняет загруженный файл в папку media/products"""
    if file.content_type not in ALLOWED_IMAGES_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла"
        )
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает допустимый размер"
        )
    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / filename
    file_path.write_bytes(content)
    return f"/media/products/{filename}"

    
def remove_product_image(url : str):
    """Удаляет файл из папки media/products"""
    if not url:
        return
    relative_path = url.lstrip("/")
    file_path = BASE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()
        







@router.get("/", response_model = ProductList)
async def get_active_products(
    page : int = Query(1, ge=1),
    page_size : int = Query(5),
    search : str | None = Query(None, min_length=1, description="Поиск товаров по названию"),
    category_id : int | None = Query(None, description="Категория для товаров"),
    min_price : float | None = Query(None, ge=0, description="Минимальная цена" ),
    max_price : float | None = Query(None, ge=0, description="Максимальная цена"),
    seller_id : int | None = Query(None, ge=0, description="ID продавца или фильтрация"),
    is_active : bool | None = Query(None, description="True актианые товары / False товары не в наличии"),
    db : AsyncSession = Depends(get_async_db)
) -> ProductList:
    
    

    filters = [ProductModel.is_active == True]
    if category_id is not None:
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= min_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)
    if is_active is not None:
        filters.append(ProductModel.is_active == is_active)
 

    rank_col = None
    if search is not None:
        search_value = search.strip()
        if search_value:
            ts_query_en = func.websearch_to_tsquery('english', search_value)
            ts_query_ru = func.websearch_to_tsquery('russian', search_value)  
            filters.append(or_(
                ProductModel.tsv.op("@@")(ts_query_en),
                ProductModel.tsv.op("@@")(ts_query_ru)
            ))

            rank_col = func.greatest(
                func.ts_rank_cd(ProductModel.tsv, ts_query_en),
                func.ts_rank_cd(ProductModel.tsv, ts_query_ru)
            )  
            

    #каунт после всех проверок
    product_total_request = await db.execute(select(func.count(ProductModel.id)).where(*filters))
    total = product_total_request.scalar()
     
    if rank_col is not None:
        products_request = await db.scalars(
            select(ProductModel)
            .join(ProductModel.category)
            .where(*filters)
            .where( CategoryModel.is_active == True)
            .offset((page - 1) * page_size)
            .options(
                selectinload(ProductModel.reviews.and_(ReviewModel.is_active == True))
            )
            .order_by(desc(rank_col), ProductModel.id)
            .limit(page_size)            
        )
        result = products_request.all()
        items = [row for row in result]
       
    else:
        products_request = await db.scalars(
            select(ProductModel)
            .join(ProductModel.category)
            .where(*filters)
            .where(CategoryModel.is_active == True)
            .offset((page - 1) * page_size)
            .options(
                selectinload(ProductModel.reviews.and_(ReviewModel.is_active == True))
            )
            .order_by(ProductModel.id)
            .limit(page_size)            
        )
        items = products_request.all()

    
    return {
        "items" : items,
        "total" : total,
        "page" : page,
        "page_size" : page_size

    }
     
 
    
@router.post("/", response_model = Product, status_code=status.HTTP_201_CREATED)
async def new_product(
    new_product : ProductCreate = Depends(ProductCreate.as_form),
    image : UploadFile | None = File(None),
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(can_manage)
) -> Product:
    request_category = await db.scalars(select(CategoryModel).where(CategoryModel.id == new_product.category_id, CategoryModel.is_active == True))
    category = request_category.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Указанная категория товара не найдена")
    
    if image is not None:
        image_url = await save_image(image)
    product = ProductModel(
        **new_product.model_dump(),
        seller_id = current_user.id,
        image_url = image_url
    )
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
async def update_product(
    product_id : int,
    new_product : ProductCreate = Depends(ProductCreate.as_form),
    image : UploadFile | None = File(None),
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(can_manage)
) -> Product:
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
    if image:
        remove_product_image(product.image_url)
        product.image_url = await save_image(image)

    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**new_product.model_dump()))
async def deactivation_status_product(product_id : int, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(can_manage)) -> Product:
    request_product = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = request_product.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Товар не найден")
    if current_user.role == "seller":
        if product.seller_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только админ или владец товара может его удалить!")
        
    remove_product_image(product.image_url)

    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active = False))
    await db.commit()
    await db.refresh(product)
    return product


 