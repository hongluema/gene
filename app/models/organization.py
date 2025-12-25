from datetime import datetime
from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.base import BaseLIMS


class Organization(BaseLIMS):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    open_to_wxapp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
