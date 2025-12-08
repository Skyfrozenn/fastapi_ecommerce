from fastapi import Depends

from app.models import UserModel
# Импортируем готовые объекты из core.py (они уже созданы)
from app.validation.core import (
    
    refresh_token_validate,
    access_token_update,
    refresh_token_update,
    access_token_create,
    refresh_token_create
)


 


# Функции-обертки для обновления токенов
async def get_new_access_token(
    user: UserModel = Depends(refresh_token_validate.verify_refresh_token)
):
    """
    Функция-обертка для создания нового access token.
    Получает валидированного пользователя через Depends и передает его в метод объекта.
    """
    return await access_token_update.new_access_token(user)


async def get_new_refresh_token(
    user: UserModel = Depends(refresh_token_validate.verify_refresh_token)
):
    """
    Функция-обертка для создания нового refresh token.
    Получает валидированного пользователя через Depends и передает его в метод объекта.
    """
    return await refresh_token_update.new_refresh_token(user)


async def get_new_access_token(user : UserModel = Depends(refresh_token_validate.verify_refresh_token)):
    return await access_token_update.new_access_token(user)



def get_creater_acces_token(data : dict):
    return access_token_create.create_acess_token(data)


def get_creater_refresh_token(data : dict):
    return refresh_token_create.create_refresh_token(data)