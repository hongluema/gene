from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, Enum, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Sample(Base):
    __tablename__ = "samples"

    sample_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(Enum("fullBlood", name="sample_type_enum"), nullable=False, server_default="fullBlood")
    process: Mapped[str] = mapped_column(Enum("progressing", "progressed", name="sample_process_enum"), nullable=False, server_default="progressing")
    user_id: Mapped[str] = mapped_column(String(12), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gender: Mapped[str | None] = mapped_column(Enum("male", "female", name="gender_enum"), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program_id: Mapped[str] = mapped_column(String(32), nullable=False)
    org_id: Mapped[str] = mapped_column(String(32), nullable=False)
    sample_data_id: Mapped[str] = mapped_column(String(32), nullable=True)
    sample_data_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_id: Mapped[str] = mapped_column(String(32), nullable=True)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
    receive_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    report_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    test_user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    see_user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default=text('1'))

    __table_args__ = (
        UniqueConstraint('sample_id', 'usable', name='samples_sample_id_usable_uk'),
    )