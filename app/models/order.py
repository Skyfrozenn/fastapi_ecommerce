from sqlalchemy import func, DateTime, Integer, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from datetime import datetime
from decimal import Decimal


class OrderModel(Base):
    __tablename__ = "orders"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status : Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    total_amount : Mapped[Decimal] = mapped_column(Numeric(10,2), default=0, nullable=False)
    createt_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user : Mapped["UserModel"] = relationship(back_populates="orders")
    items : Mapped[list["OrderItemModel"]] = relationship(back_populates="order")