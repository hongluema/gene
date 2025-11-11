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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
