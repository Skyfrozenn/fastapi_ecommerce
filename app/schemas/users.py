from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


class UserCreate(BaseModel):
    name : str = Field(..., min_length = 3, max_length = 20, description = "Имя пользователя от 3 до 20 символов")  
    email : EmailStr
    password : str = Field(..., min_length = 8, description = "Пароль не менее 8 символов")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value : str) -> str:
        if not any(item.isupper() for item in value):
            raise ValueError("Введите хотя бы один большой символ")
        if not any(item  in "!@#$%^&*()_+'/.," for item in value):
            raise ValueError("Введите хотя бы один специальный символ")
        return value
    

class UserSchema(BaseModel):
    id : int
    email : EmailStr
    role : str
    is_active : bool

    model_config = ConfigDict(from_attributes=True)
     

class RefreshToken(BaseModel):
    refresh_token : str



class RefreshTokenlist(BaseModel):
    refresh_tokens : list[RefreshToken] = Field(..., description="Список рефреш токенов")