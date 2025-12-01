from datetime import datetime
from sqlalchemy import Integer, String, Enum, TIMESTAMP, CheckConstraint, text, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True, onupdate=text("CURRENT_TIMESTAMP")
    )
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default='1')

    __table_args__ = (
        CheckConstraint("age > 0 AND age <= 150", name="users_chk_1"),
        UniqueConstraint('phone', 'usable', name='users_phone_usable_uk'),
        UniqueConstraint('id_number', 'usable', name='users_id_number_usable_uk'),
    )


# 为 User 模型添加默认过滤条件：usable = 1
# 导入 Session 以注册事件监听器
from sqlalchemy.orm import Session as SQLAlchemySession

# 使用 do_orm_execute 事件在 ORM 查询执行前自动添加过滤条件
@event.listens_for(SQLAlchemySession, "do_orm_execute")
def receive_do_orm_execute(execute_state):
    """自动为 User 查询添加 usable = 1 的过滤条件"""
    if execute_state.is_select and not execute_state.is_column_load and not execute_state.is_relationship_load:
        # 检查查询是否涉及 User 模型
        if hasattr(execute_state.statement, 'selected_columns'):
            # 检查查询是否包含 User 表
            froms = execute_state.statement.froms if hasattr(execute_state.statement, 'froms') else []
            if User.__table__ in froms:
                # 检查是否已经存在 usable 过滤条件
                has_usable_filter = False
                if hasattr(execute_state.statement, 'whereclause') and execute_state.statement.whereclause:
                    has_usable_filter = any('usable' in str(clause) for clause in execute_state.statement.whereclause.clauses)
                if not has_usable_filter:
                    execute_state.statement = execute_state.statement.where(User.usable == 1)