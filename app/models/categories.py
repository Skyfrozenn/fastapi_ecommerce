from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, Optional

from app.database import Base

 

class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id : Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    products : Mapped[List["ProductModel"]] = relationship(back_populates="category",  cascade="all, delete-orphan")

    children : Mapped[List["CategoryModel"]] = relationship(back_populates="parent") #связь родителя с детьми у родителя может быть много детей
    parent : Mapped[Optional["CategoryModel"]] = relationship(back_populates="children", remote_side="CategoryModel.id") #связь ребенка с родителем , ремот_сайд указывает что внешний ключ из этой же таблицы

 
