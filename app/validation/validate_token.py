import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
 

from app.database import select, AsyncSession
from app.models import UserModel
from app.db_depends import get_async_db
from app.shemas.users import RefreshToken


 

oath2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

class AccessTokenValidate:
    def __init__(self, secret_key, algorithm):
        self.__secret_key = secret_key
        self.algorithm = algorithm
    
    async def get_current_user(self, token : str = Depends(oath2_scheme), db : AsyncSession = Depends(get_async_db)):
        """
        Функция охранник проверяет акссес токен
        """
        credentals_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные!",
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.decode(token, self.__secret_key, algorithms=[self.algorithm])   
            email : str | None = payload.get("sub")
            token_types : str | None = payload.get("token_types")
            if email is None or token_types != "acess" : #если емейла нет то неверные данные пошел нахуй
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
    


class RefreshTokenValidate:
    def __init__(self, secret_key, algorithm):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def verify_refresh_token(self, token : RefreshToken, db : AsyncSession = Depends(get_async_db)):  
        credentals_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные!",
            headers={"WWW-Authenticate": "Bearer"}
        )
        try:
            
            payload = jwt.decode(token.refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            email : str | None = payload.get("sub")
            token_types : str | None = payload.get("token_types")
            if email is None or token_types != "refresh" : # 
                raise credentals_exception
        except jwt.ExpiredSignatureError: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Время токена истекло!",
                headers={"WWW-Authenticate" : "Bearer"}
            )
        except jwt.PyJWTError: 
            raise credentals_exception
        request_user = await db.scalars(
            select(UserModel)
            .where(UserModel.email == email, UserModel.is_active == True)
        )
        user = request_user.first()
        if user is None:
            raise credentals_exception
        return user

    
    
