from sqlalchemy import ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from decimal import Decimal


class OrderItemModel(Base):
    __tablename__ = "orderitems"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id : Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id : Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity : Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_product : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price_cart : Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order : Mapped["OrderModel"] = relationship(back_populates="items")
    product : Mapped["ProductModel"] = relationship(back_populates="order_item_products")



