"""
Центральное место для создания всех объектов токенов.
Все объекты создаются один раз при импорте модуля.
"""
from app.validation.create_token import AcessTokenCreate, RefreshTokenCreate
from app.validation.update_token import AccessTokenUpdate, RefreshTokenUpdate
from app.validation.validate_token import AccessTokenValidate, RefreshTokenValidate

from app.validation.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCES_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS    
)

# Глобальные объекты создаются один раз при старте приложения

# Объекты для создания токенов
access_token_create = AcessTokenCreate(
    algorithm=ALGORITHM,
    secret_key=SECRET_KEY,
    acces_token_expire_minutes=ACCES_TOKEN_EXPIRE_MINUTES
)

refresh_token_create = RefreshTokenCreate(
    algorithm=ALGORITHM,
    secret_key=SECRET_KEY,
    refresh_token_expire_days=REFRESH_TOKEN_EXPIRE_DAYS
)

# Объекты для валидации токенов
access_token_validate = AccessTokenValidate(
    algorithm=ALGORITHM,
    secret_key=SECRET_KEY,
)

refresh_token_validate = RefreshTokenValidate(
    algorithm=ALGORITHM,
    secret_key=SECRET_KEY,
)

# Объекты для обновления токенов (зависят от create и validate)
access_token_update = AccessTokenUpdate(
    creater=access_token_create     
)

refresh_token_update = RefreshTokenUpdate(
    creater=refresh_token_create     
)

