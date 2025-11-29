 
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from app.database import select, AsyncSession
from app.models import UserModel
from app.db_depends import get_async_db
from app.config import SECRET_KEY, ALGORITHM

ACCES_TOKEN_EXPIRE_MINUTES = 30
oath2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password : str) -> str:
    """
    Генерирует пароль в ХЕШ
    с использованием bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password : str, hash_password : str) -> bool:
    """
    Проверяет соответсвует ли введеный пароль хешу в бд
    """
    return pwd_context.verify(plain_password, hash_password)


def create_acess_token(data : dict):
    to_encody = data.copy() #копируем словарь с данными чтобы не испортить оригинал

    exprire = datetime.now(timezone.utc) + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES) #текущее время + 30 минут

    to_encody["exp"] = exprire #добавляем в словарь

    return jwt.encode(to_encody, SECRET_KEY, algorithm=ALGORITHM) #полезная нагрузка, секретный ключ алгоритм для подписи , весь jwt


async def get_current_user(token : str = Depends(oath2_scheme), db : AsyncSession = Depends(get_async_db)):
    """
    Функция охранник проверяет акссес токен
    """
    credentals_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные!",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  #Декодируем джвт токен , извлекаем емейл
        email : str = payload.get("sub")
        if email is None: #если емейла нет то неверные данные пошел нахуй
            raise credentals_exception
    except jwt.ExpiredSignatureError: #проверка не истекло ли время если да нахуй пошел
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Время токена истекло!",
            headers={"WWW-Authenticate" : "Bearer"}
        )
    except jwt.PyJWTError: #проверка подписи хуедписи всякой хуйни всего джвт 
        raise credentals_exception
    request_user = await db.scalars(
        select(UserModel)
        .where(UserModel.email == email, UserModel.is_active == True)
    )
    user = request_user.first() 
    if user is None: #если юзера нет в бд то тоже идет нахуй
        raise credentals_exception
    return user



async def get_seller_user(current_user : UserModel = Depends(get_current_user)): #проверка для продавца
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Ограничено в доступе, доступ разрешен только продавцу товара"
        )
    return current_user


async def can_manage(current_user : UserModel = Depends(get_current_user)): #для удаления товаров
    if current_user.role != "seller" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только продавцу товара и администратору!"
        )
    return current_user

async def get_admin_user(current_user : UserModel = Depends(get_current_user)): #для круд категорий просмотра статистики и эндпоинтов только для админов
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам!"
        )
    return current_user
