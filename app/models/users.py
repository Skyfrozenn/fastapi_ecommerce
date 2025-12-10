from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    email : Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password : Mapped[str] = mapped_column(String, nullable = False)
    is_active : Mapped[bool] = mapped_column(Boolean, default = True)
    role : Mapped[str] = mapped_column(String, default = "admin")

    products : Mapped[list["ProductModel"]] = relationship(back_populates="seller")
    reviews : Mapped[list["ReviewModel"]] = relationship(back_populates="user")