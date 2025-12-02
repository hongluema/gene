from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, Enum, text, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Sample(Base):
    __tablename__ = "samples"

    sample_id: Mapped[str] = mapped_column(String(32), primary_key=True) # 样品id
    code: Mapped[str] = mapped_column(String(255), nullable=False) # 血管的编码
    name: Mapped[str] = mapped_column(String(255), nullable=False) # 检测人的姓名
    type: Mapped[str] = mapped_column(Enum("fullBlood", name="sample_type_enum"), nullable=False, server_default="fullBlood") # 样本类型。默认是全血
    process: Mapped[str] = mapped_column(Enum("progressing", "progressed", name="sample_process_enum"), nullable=False, server_default="progressing") # 样本状态。默认是检测中
    user_id: Mapped[str] = mapped_column(String(12), nullable=False) # 录入人的user_id
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True) # 检测人的手机号
    id_number: Mapped[str | None] = mapped_column(String(32), nullable=True) # 检测人的身份证号
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True) # 检测人的性别
    age: Mapped[int | None] = mapped_column(Integer, nullable=True) # 检测人的年龄
    program_id: Mapped[str] = mapped_column(String(32), nullable=False) # 项目id
    org_id: Mapped[str] = mapped_column(String(32), nullable=False) # 机构id
    sample_data_id: Mapped[str] = mapped_column(String(32), nullable=True) # 样本数据id
    sample_data_name: Mapped[str | None] = mapped_column(String(255), nullable=True) # 样本数据名称
    order_id: Mapped[str] = mapped_column(String(32), nullable=True) # 订单id
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True) # 描述
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False, onupdate=text("CURRENT_TIMESTAMP")
    )
    receive_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True) # 接收时间
    report_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True) # 报告完成时间
    test_user: Mapped[str | None] = mapped_column(String(100), nullable=True) # 检测人
    see_user: Mapped[str | None] = mapped_column(String(100), nullable=True) # 审核人
    mongoid: Mapped[str | None] = mapped_column(String(100), nullable=True) # mongodb的id
    usable: Mapped[int] = mapped_column(Integer, nullable=True, server_default=text('1'))

    __table_args__ = (
        UniqueConstraint('sample_id', 'usable', name='samples_sample_id_usable_uk'),
    )


# 为 Sample 模型添加默认过滤条件：usable = 1
# 导入 Session 以注册事件监听器
from sqlalchemy.orm import Session as SQLAlchemySession

# 使用 do_orm_execute 事件在 ORM 查询执行前自动添加过滤条件
@event.listens_for(SQLAlchemySession, "do_orm_execute")
def receive_sample_do_orm_execute(execute_state):
    """自动为 Sample 查询添加 usable = 1 的过滤条件"""
    if execute_state.is_select and not execute_state.is_column_load and not execute_state.is_relationship_load:
        # 检查查询是否涉及 Sample 模型
        if hasattr(execute_state.statement, 'selected_columns'):
            # 检查查询是否包含 Sample 表
            froms = execute_state.statement.froms if hasattr(execute_state.statement, 'froms') else []
            if Sample.__table__ in froms:
                # 检查是否已经存在 usable 过滤条件
                has_usable_filter = False
                if hasattr(execute_state.statement, 'whereclause') and execute_state.statement.whereclause:
                    has_usable_filter = any('usable' in str(clause) for clause in execute_state.statement.whereclause.clauses)
                if not has_usable_filter:
                    execute_state.statement = execute_state.statement.where(Sample.usable == 1)