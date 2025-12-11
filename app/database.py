from sqlalchemy import create_engine, select, update,func, desc
from sqlalchemy.orm import Session,DeclarativeBase, joinedload

DATABASE_URL = "sqlite:///ecommerse.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = Session(bind=engine)

 

# Асинхрронное подключение-----------------------------------------------------------------------
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv


load_dotenv() #чтобы загружать из переменных env

DATABASE_URL = os.getenv("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL, echo = True, execution_options={"autocommit": False})
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

 

 


