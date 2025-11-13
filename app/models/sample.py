from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sample(Base):
    __tablename__ = "samples"

    sample_id: Mapped[str] = mapped_column(String(12), primary_key=True, index=True)
    sample_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(Enum("fullBlood", name="sample_type_enum"), nullable=False, server_default="fullBlood")
    process: Mapped[str] = mapped_column(Enum("progressing", "progressed", name="sample_process_enum"), nullable=False, server_default="progressing")
    user_id: Mapped[str] = mapped_column(String(12), ForeignKey("users.user_id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(12), ForeignKey("projects.project_id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(12), ForeignKey("organizations.organization_id"), nullable=False)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
