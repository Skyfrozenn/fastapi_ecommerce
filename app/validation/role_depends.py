from fastapi import Depends, HTTPException, status

from app.models import UserModel
# Импортируем готовые объекты из core.py (они уже созданы)
from app.validation.core import access_token_validate


async def get_seller_user(
    current_user: UserModel = Depends(access_token_validate.get_current_user)
):
    """Проверка для продавца"""
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ограничено в доступе, доступ разрешен только продавцу товара"
        )
    return current_user


async def can_manage(
    current_user: UserModel = Depends(access_token_validate.get_current_user)
):
    """Для удаления товаров - доступ продавцу и администратору"""
    if current_user.role != "seller" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только продавцу товара и администратору!"
        )
    return current_user


async def get_admin_user(
    current_user: UserModel = Depends(access_token_validate.get_current_user)
):
    """Для CRUD категорий, просмотра статистики и эндпоинтов только для админов"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам!"
        )
    return current_user

     