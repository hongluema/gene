from datetime import datetime
from sqlalchemy import Integer, String, TIMESTAMP, text, UniqueConstraint, event, Enum
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Apply(Base):
    __tablename__ = "applies"

    apply_id: Mapped[str] = mapped_column(String(32), primary_key=True) # 申请id
    apply_user_id: Mapped[str] = mapped_column(String(50), nullable=False) # 申请人user_id
    apply_user_phone: Mapped[str | None] = mapped_column(String(32), nullable=True) # 申请人手机号
    sample_id: Mapped[str] = mapped_column(String(32), nullable=False) # 样本id
    type: Mapped[int] = mapped_column(Integer, nullable=False) # 申请类型。1是作废，2是修改
    status: Mapped[str] = mapped_column(Enum("pending", "approved", "rejected", name="apply_status_enum"), nullable=False, server_default="pending") # 申请状态。pending-待审批, approved-通过, rejected-拒绝
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True) # 申请原因
    reviewer_id: Mapped[str | None] = mapped_column(String(50), nullable=True) # 审批人user_id
    review_time: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True) # 审批时间
    review_comment: Mapped[str | None] = mapped_column(String(500), nullable=True) # 审批意见
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default=text('1'))

    __table_args__ = (
        UniqueConstraint('sample_id', 'usable', name='applies_sample_id_usable_uk'),
    )


# : Apply !���ؤ��a�usable = 1
# �e Session �茋��,h
from sqlalchemy.orm import Session as SQLAlchemySession

# ( do_orm_execute ��( ORM ��gLM�����a�
@event.listens_for(SQLAlchemySession, "do_orm_execute")
def receive_apply_do_orm_execute(execute_state):
    """�: Apply ���� usable = 1 ���a�"""
    if execute_state.is_select and not execute_state.is_column_load and not execute_state.is_relationship_load:
        # ����/&�� Apply !�
        if hasattr(execute_state.statement, 'selected_columns'):
            # ����/&+ Apply h
            froms = execute_state.statement.froms if hasattr(execute_state.statement, 'froms') else []
            if Apply.__table__ in froms:
                # ��/&��X( usable ��a�
                has_usable_filter = False
                if hasattr(execute_state.statement, 'whereclause') and execute_state.statement.whereclause is not None:
                    # t* whereclause lb:W&2e��/&+ usable
                    has_usable_filter = 'usable' in str(execute_state.statement.whereclause)
                if not has_usable_filter:
                    execute_state.statement = execute_state.statement.where(Apply.usable == 1)
