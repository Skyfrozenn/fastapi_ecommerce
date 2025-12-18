from sqlalchemy import DateTime, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datetime import datetime

from app.database import Base



class CartModel(Base):
    __tablename__ = "carts"
    
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
    )

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False, index=True)
    product_id : Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"),nullable=False, index=True)
    quantity : Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user : Mapped["UserModel"] = relationship(back_populates="cart_item")
    product : Mapped["ProductModel"] = relationship(back_populates="cart_item")

