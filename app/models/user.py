from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mobile: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    nickname: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # password: Mapped[str] = mapped_column(String(255), nullable=False)
