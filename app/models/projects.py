from ast import In
from audioop import mul
from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import BaseLIMS


class Project(BaseLIMS):
    __tablename__ = "program"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=False, autoincrement='auto')
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    code: Mapped[str] = mapped_column(String(100), nullable=True)
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default=1)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    create_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True, onupdate=text("CURRENT_TIMESTAMP")
    )
    p_type_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=True)
    cost: Mapped[Decimal] = mapped_column(Decimal(20, 9), nullable=True )
    coder_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=True)
