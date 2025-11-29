from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models import UserModel
from app.shemas.users import UserCreate, UserSchema
from app.database import AsyncSession, select, update
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_acess_token

 

router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def new_user(user_create : UserCreate, db : AsyncSession = Depends(get_async_db)) -> UserSchema:
    request_user = await db.scalars(select(UserModel).where(UserModel.email == user_create.email))
    user = request_user.first()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email занят!")
    new_user = UserModel(
        email = user_create.email,
        hashed_password = hash_password(user_create.password),
        role = user_create.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
        


@router.post("/token")
async def login(form_data : OAuth2PasswordRequestForm = Depends(), db : AsyncSession = Depends(get_async_db)):
    request_user = await db.scalars(
        select(UserModel)
        .where(UserModel.email == form_data.username, UserModel.is_active == True)
    )
    user = request_user.first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный пароль или емейл, или юзер не активен",
            headers={"WWW-Authenticate" : "Bearer"}
        )
    data = {
        "sub" : user.email,
        "role" : user.role,
        "id" : user.id
    }
    access_token = create_acess_token(data)
    return {"access_token": access_token, "token_type": "bearer"}