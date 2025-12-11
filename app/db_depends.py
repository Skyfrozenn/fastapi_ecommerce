from sqlalchemy.orm import Session
from app.database import SessionLocal
from collections.abc import Generator, AsyncGenerator


def get_db() -> Generator[Session, None,None]:
    db : Session = SessionLocal
    try:
        yield db
    finally:
        db.close()




#асинхрнная версия генератора сессий
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from collections.abc import AsyncGenerator


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session: # 1. Создание сессии и начало транзакции
        try:
            yield session # 2. Передача сессии в эндпоинт/сервис
            await session.commit() # 3. Попытка коммита после успешного выполнения эндпоинта
        except Exception as e:
            await session.rollback() # 4. Откат при любой ошибке
            print(f"DEBUG: Transaction rolled back due to error: {e}")
            raise # 5. Перевыброс ошибки



