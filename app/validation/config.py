import os
from dotenv import load_dotenv

from app.validation.jwt_manager import JWTManager


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

jwtmanager = JWTManager(
    algorithm = ALGORITHM,
    secret_key = SECRET_KEY,
    acces_token_expire_minutes = ACCES_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
)
