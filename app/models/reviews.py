from sqlalchemy import select, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Optional

from app.database import Base


class ReviewModel(Base):
    __tablename__ = "reviews"
    
    id : Mapped[int] = mapped_column(Integer, primary_key = True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable = False)
    product_id : Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable = False)
    comment : Mapped[Optional[str]] = mapped_column(Text, default=None, nullable = True)
    comment_date : Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    grade : Mapped[int] = mapped_column(Integer, nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default = True)

    user : Mapped["UserModel"] = relationship(back_populates="reviews")
    product : Mapped["ProductModel"] = relationship(back_populates="reviews")

