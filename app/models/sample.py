from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, Enum, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sample(Base):
    __tablename__ = "samples"

    sample_id: Mapped[str] = mapped_column(String(12), primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(Enum("fullBlood", name="sample_type_enum"), nullable=False, server_default="fullBlood")
    process: Mapped[str] = mapped_column(Enum("progressing", "progressed", name="sample_process_enum"), nullable=False, server_default="progressing")
    user_id: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    sex: Mapped[str | None] = mapped_column(Enum("male", "female", name="sex_enum"), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    org_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    sample_data_id: Mapped[int] = mapped_column(BigInteger, index=True)
    order_id: Mapped[int] = mapped_column(BigInteger, index=True)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
