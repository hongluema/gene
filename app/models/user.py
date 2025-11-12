from datetime import datetime
from sqlalchemy import Integer, String, Enum, TIMESTAMP, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    openid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    idCard: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    sex: Mapped[str | None] = mapped_column(Enum("male", "female", name="sex_enum"), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True, onupdate=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint("age > 0 AND age <= 150", name="users_chk_1"),
    )
