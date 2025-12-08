

# Импортируем функции-обертки из depends.py
from app.validation.depends import (
    get_new_access_token,
    get_new_refresh_token,
    get_creater_acces_token,
    get_creater_refresh_token
   
)

from app.validation.hash_password import hash_password, verify_password

from app.validation.role_depends import can_manage, get_seller_user, get_admin_user

# Экспортируем для удобного использования
__all__ = [
    get_new_access_token,
    get_new_refresh_token,
    get_creater_acces_token,
    get_creater_refresh_token,
    hash_password, verify_password,
    can_manage, get_seller_user, get_admin_user
 
]


