from datetime import datetime
from sqlalchemy import BigInteger, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    org_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
