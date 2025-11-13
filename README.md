# Gene FastAPI 项目脚手架

一个基于 FastAPI + SQLAlchemy 的后端项目模板，数据库使用 MySQL（账号、密码、地址先用占位符，见 `.env.example`）。包含示例用户模型与基础 CRUD 接口，可直接启动与访问。

## 特性

- FastAPI 应用入口与自动生成 OpenAPI 文档（/docs, /redoc）
- SQLAlchemy 2.x + PyMySQL 连接 MySQL
- 开发模式自动建表（生产建议使用 Alembic 迁移）
- 简单示例：用户的创建/查询接口
- `.env` 配置管理，包含 CORS 支持

## 目录结构

```
.
project/
├── main.py
├── app/
│   ├── __init__.py
│   ├── api/              # 路由层（接口定义）
│   │   ├── __init__.py
│   │   ├── v1/           # 版本 1 接口
│   │   │   ├── endpoints/
│   │   │   │   ├── user.py
│   │   │   │   └── item.py
│   │   └── dependencies.py  # 依赖项（如数据库会话）
│   ├── core/             # 核心配置（数据库连接、全局参数等）
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/           # ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/          # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   └── crud/             # 数据访问层（CRUD）
│       ├── __init__.py
│       ├── base.py       # 通用 CRUD 基类（如增删改查模板）
│       ├── user.py       # 用户 CRUD（继承基类）
│       └── item.py       # 商品 CRUD（继承基类）
├─ .env.example                 # 环境变量示例（复制为 .env 并填写）
├─ requirements.txt             # Python 依赖
└─ README.md
```

## 快速开始

### 1) 环境准备

- Python 版本：3.10+（建议 3.11）
- 安装依赖：

```bash
# 创建虚拟环境（macOS / Linux）
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
# py -3 -m venv .venv
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
```

### 2) 配置数据库连接

复制 `.env.example` 为 `.env` 并填写内容：

```
DATABASE_URL="mysql+pymysql://<USER>:<PASSWORD>@<HOST>:3306/<DB_NAME>?charset=utf8mb4"
APP_NAME="Gene API"
APP_ENV="development"
APP_HOST="127.0.0.1"
APP_PORT="8000"
APP_RELOAD="true"
CORS_ORIGINS="*"
```

示例（本地 MySQL）：

```
DATABASE_URL="mysql+pymysql://root:root@127.0.0.1:3306/gene_db?charset=utf8mb4"
```

如果你需要一个临时的 MySQL（Docker）：

```bash
docker run --name gene-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=gene_db -p 3306:3306 -d mysql:8
```

> 开发模式下，应用启动时会自动建表；生产建议使用 Alembic 做结构迁移。

### 3) 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- 健康检查: http://127.0.0.1:8000/api/health

## 示例接口

- 创建用户

```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{"mobile": "18200000000", "nickname": "Tester", "avatar": ""}'
```

- 查询用户列表（支持分页：skip, limit<=100，按 id 倒序）

```bash
curl "http://127.0.0.1:8000/api/users/?skip=0&limit=20"
```

- 查询用户详情

```bash
curl "http://127.0.0.1:8000/api/users/1"
```

返回示例：

```json
{
  "id": 1,
  "mobile": "18200000000",
  "nickname": "Tester",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 重要说明

- 开发便捷性：当前在应用启动时通过 `Base.metadata.create_all` 自动建表，适合快速验证。生产环境请接入 Alembic 迁移。
- 同步 SQLAlchemy：本模板使用 SQLAlchemy 同步引擎 + `SessionLocal`。如果需要全链路异步，请切换为 `sqlalchemy[asyncio]` + `asyncmy/aiomysql`，并改造依赖和路由为 async 版本。
- CORS：通过环境变量 `CORS_ORIGINS` 配置（逗号分隔）。生产环境请设置为明确的域名白名单。

## 常见问题

- 连接失败：请检查 `DATABASE_URL` 是否正确（用户名、密码、主机、端口、数据库名），以及 MySQL 是否允许外部连接。
- 字符集：连接串默认带 `?charset=utf8mb4`，能覆盖绝大多数场景。
- 端口占用：如 `8000` 被占用，修改启动命令中的 `--port` 或 `.env` 中的 `APP_PORT`（后者仅作为参考，不会自动作用于命令）。

## 下一步（可选）

- 集成 Alembic：结构迁移与版本管理
- 增加日志配置、错误码与统一响应结构
- 引入测试框架（pytest）与 CI
- 鉴权（JWT / OAuth2）与用户密码模型

CREATE TABLE users (
user_id VARCHAR(50) NOT NULL UNIQUE COMMENT '用户唯一标识（字符串）',
openid VARCHAR(100) NOT NULL UNIQUE COMMENT '第三方平台唯一标识（如微信 openid）',
name VARCHAR(128) COMMENT '用户姓名',
nickname VARCHAR(255) COMMENT '微信昵称',
avatar VARCHAR(255) COMMENT '微信头像',
mobile VARCHAR(32) UNIQUE COMMENT '用户手机号（允许为 NULL，根据业务需求可调整为 NOT NULL）',
idCard VARCHAR(32) UNIQUE COMMENT '用户身份证号（允许为 NULL，根据业务需求可调整为 NOT NULL）',
sex ENUM('male', 'female') COMMENT '性别（male：男，female：女，允许为 NULL 表示未填写）',
age INT CHECK (age > 0 AND age <= 150) COMMENT '年龄（约束为合理范围：1-150 岁）',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
PRIMARY KEY (user_id) -- 以 user_id 为主键，确保唯一性和查询效率
);

<!-- create table prompt -->

> 第一步
> 将这个给我改成一个 organizations 表，字段有：organization_id(字符串)，name（字符串），desc（字符串），created_at（时间默认创建记录的时候，后续不再更新）,updated_at(默认当前时间，每次更新),created_at 和 updated_at 都不允许为空，自动填充，name 也不允许，desc 允许，organization_id 长度为 12，以 o 开头，剩余 11 为随机数
> 第二步
> 按照 projects 的 model，完善 crud 的 proejcts 文件和 schemas 目录的 projects 文件
