from datetime import datetime
from sqlalchemy import Integer, String, Enum, TIMESTAMP, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    gender: Mapped[str | None] = mapped_column(Enum("male", "female", name="gender_enum"), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True, onupdate=text("CURRENT_TIMESTAMP")
    )
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default='1')

    __table_args__ = (
        CheckConstraint("age > 0 AND age <= 150", name="users_chk_1"),
    )
