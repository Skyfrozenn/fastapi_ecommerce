from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Numeric,ForeignKey, Float, Index, Computed
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy.dialects.postgresql import TSVECTOR

from typing import List


from app.database import Base

class ProductModel(Base):
    __tablename__ = "products"
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description : Mapped[str | None] = mapped_column(String(500), nullable=True)
    price : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url : Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock : Mapped[int] = mapped_column(Integer, nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default = True)
    category_id : Mapped[int] = mapped_column(Integer, ForeignKey("categories.id",  ondelete="CASCADE"), nullable=False)
    seller_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False)
    rating : Mapped[float] = mapped_column(Float, default = 0.0, nullable = False)

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            || setweight(to_tsvector('russian', coalesce(name, '')), 'A')
            || setweight(to_tsvector('english', coalesce(description, '')), 'B')
            || setweight(to_tsvector('russian', coalesce(description, '')), 'B')
            """,
            persisted=True,
        ),
        nullable=False,
    )
    category : Mapped["CategoryModel"] = relationship(back_populates="products")
    seller : Mapped["UserModel"] = relationship(back_populates="products")
    reviews : Mapped[list["ReviewModel"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    cart_item : Mapped[list["CartModel"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
         
    )