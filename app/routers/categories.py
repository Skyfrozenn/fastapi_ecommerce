from fastapi import APIRouter,Depends, status, HTTPException


from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.schemas.categories import Category, CategoryCreate
 
from app.models import CategoryModel, UserModel
from app.db_depends import  get_async_db
from app.validation.role_depends import get_admin_user



router = APIRouter(
    prefix = "/category",
    tags = ["categories"]
)

@router.get("/", response_model = List[Category])
async def get_all_categories(db : AsyncSession = Depends(get_async_db)) -> List[Category]:
    all_category = await db.scalars(select(CategoryModel).where(CategoryModel.is_active == True).order_by(CategoryModel.id.asc())) #ожидаем висит задача пока не выполнится
    result = all_category.all() #как выполнилась ток тогда ебашим
    return result

     




@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def creat_category(category : CategoryCreate,  db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)) -> Category:
    if category.parent_id is not None:
        request_parent =  await db.execute(select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active == True))
        parent = request_parent.scalar()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent Category не найдна!")
    
    new_category = CategoryModel(**category.model_dump())
    db.add(new_category)

    await db.commit()
    await db.refresh(new_category)
    return new_category

     
 
@router.put("/{category_id}", response_model=Category)
async def update_category(category_id : int, new_category : CategoryCreate, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_category =  await db.execute(select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True))
    category = request_category.scalar()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена!")
    if new_category.parent_id is not None:
        request_parent = await  db.execute(select(CategoryModel).where(CategoryModel.id == new_category.parent_id, Category.is_active == True))
        parent = request_parent.scalar()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория родителя не найдена!")
        
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(**new_category.model_dump()))
    await db.commit()

    return category
     


 
@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id : int, db : AsyncSession = Depends(get_async_db), current_user : UserModel = Depends(get_admin_user)):
    request_category = await db.execute(select(CategoryModel).where(CategoryModel.id == category_id))
    category = request_category.scalar()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    if category.parent_id is None:
        await db.execute(update(CategoryModel).where(CategoryModel.parent_id == category.id).values(is_active = False))
        
    
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active = False))
    await db.commit()
    return {"status": "success", "message": "Category marked as inactive"}
     