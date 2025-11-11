from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 连接 URL 格式：
# mysql+pymysql://用户名:密码@主机地址:端口号/数据库名?charset=utf8mb4
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://walry:arApp123qwe..@117.149.9.79:33060/applet_wy?charset=utf8mb4"

# 创建数据库引擎（echo=True 会打印 SQL 语句，调试用）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # 生产环境可关闭
    pool_pre_ping=True  # 检测连接有效性，避免断开
)

# 创建会话工厂（用于生成数据库会话）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类（所有模型类继承该类）
Base = declarative_base()