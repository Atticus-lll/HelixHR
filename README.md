# AI驱动的人力资源系统 · AI-Driven Human Resources System (HelixHR)

> 基于 FastAPI + MySQL + ChromaDB 构建的 AI 驱动型人力资源系统，支持 RBAC 权限控制、JWT 认证与 RAG 智能知识检索。

---

## 功能特性

### 核心功能
- **员工管理**: 完整的 CRUD 操作，支持分页、筛选、排序
- **部门管理**: 树形部门结构，支持多级部门
- **薪资管理**: 月度薪资录入、编辑、查询，含自动计算
- **角色权限**: 基于 RBAC 的细粒度权限控制
- **RAG 知识库**: 文档上传、向量化、自然语言检索

### 企业级特性
- **JWT 认证**: HS256 算法，支持 Token 自动过期
- **请求限流**: 基于 IP 的访问频率限制
- **统一异常处理**: 标准化的错误响应格式
- **日志追踪**: 结构化日志，支持文件轮转
- **数据库迁移**: Alembic 版本化管理
- **容器化部署**: Docker + docker-compose 一键启动

---

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 |
| 迁移工具 | Alembic |
| 验证 | Pydantic v2 |
| 认证 | JWT (python-jose) + bcrypt |
| 嵌入模型 | sentence-transformers |
| 向量数据库 | ChromaDB |
| 日志 | loguru |
| 容器化 | Docker |
| 测试 | pytest |

---

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Docker & Docker Compose（可选）

### 1. 克隆并安装依赖

`ash
git clone <repository-url>
cd enterprise-employee-management
pip install -r requirements.txt
`

### 2. 配置数据库

复制配置文件：

`ash
cp .env.example .env
# 编辑 .env 中的配置
`

### 3. 初始化数据库

`ash
python scripts/init_db.py
`

该脚本将：
- 创建所有数据库表
- 创建默认角色（系统管理员、人事专员、普通员工）
- 创建默认管理员账号：dmin / dmin123456
- 创建默认部门（技术部、人力资源部、销售部、财务部）

### 4. 启动服务

**开发模式：**

`ash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
`

**生产模式（使用 Docker）：**

`ash
docker-compose up --build -d
`

服务启动后访问：
- API 文档: http://localhost:8001/docs
- ReDoc 文档: http://localhost:8001/redoc
- 健康检查: http://localhost:8001/health

---

## Docker 部署

### 使用 Docker Compose（推荐）

`ash
docker-compose up --build -d
`

这将启动：
- mysql: MySQL 8.0 数据库容器
- pp: FastAPI 应用容器

---

## API 接口文档

### 认证接口

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/auth/login | POST | 用户登录 | 公开 |
| /api/v1/auth/register | POST | 注册用户 | 管理员 |
| /api/v1/auth/me | GET | 当前用户信息 | 登录用户 |

### 员工管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/employees | GET | 员工列表（分页） | 登录用户 |
| /api/v1/employees | POST | 新增员工 | 人事专员 |
| /api/v1/employees/{id} | GET | 员工详情 | 登录用户 |
| /api/v1/employees/{id} | PUT | 更新员工 | 人事专员 |
| /api/v1/employees/{id} | DELETE | 删除员工 | 管理员 |

### 部门管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/departments | GET | 部门列表 | 登录用户 |
| /api/v1/departments | POST | 新增部门 | 管理员 |
| /api/v1/departments/{id} | GET | 部门详情 | 登录用户 |
| /api/v1/departments/{id} | PUT | 更新部门 | 管理员 |
| /api/v1/departments/{id} | DELETE | 删除部门 | 管理员 |

### 薪资管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/salaries | GET | 薪资记录列表 | 人事专员 |
| /api/v1/salaries | POST | 录入薪资 | 人事专员 |
| /api/v1/salaries/{id} | PUT | 更新薪资 | 人事专员 |
| /api/v1/salaries/employee/{emp_id} | GET | 员工薪资历史 | 人事专员 |

### 角色管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/roles | GET | 角色列表 | 管理员 |
| /api/v1/roles | POST | 创建角色 | 管理员 |
| /api/v1/roles/{id} | PUT | 更新角色 | 管理员 |
| /api/v1/roles/{id} | DELETE | 删除角色 | 管理员 |

### RAG 知识检索

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| /api/v1/rag/query | POST | 自然语言检索 | 管理员 |
| /api/v1/rag/documents/upload | POST | 上传文档（.txt/.md） | 管理员 |
| /api/v1/rag/documents/text | POST | 提交文本内容 | 管理员 |
| /api/v1/rag/documents | GET | 文档列表 | 管理员 |
| /api/v1/rag/documents/{id} | DELETE | 删除文档 | 管理员 |
| /api/v1/rag/stats | GET | 统计信息 | 管理员 |

---

## 项目结构

`
helix-hr/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理（YAML + ENV）
│   ├── api/                 # API 路由层
│   │   ├── deps.py         # 依赖注入
│   │   └── v1/             # v1 API 版本
│   ├── core/               # 核心模块
│   │   ├── security.py     # JWT + 密码工具
│   │   ├── exceptions.py   # 自定义异常
│   │   └── pagination.py   # 分页工具
│   ├── models/             # SQLAlchemy 模型层
│   ├── schemas/            # Pydantic Schema 层
│   ├── services/           # 业务逻辑层
│   ├── repositories/       # 数据访问层
│   ├── rag/                # RAG 模块
│   └── utils/              # 日志配置
├── alembic/                # 数据库版本管理
├── tests/                  # 测试
├── scripts/
│   └── init_db.py         # 数据库初始化
├── config.yaml             # 主配置文件
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
`

---

## RAG 模块使用

### 方式一：上传文档

`ash
curl -X POST "http://localhost:8001/api/v1/rag/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@员工手册.txt" \
  -F "title=员工手册v1.0" \
  -F "source=HR部门"
`

### 方式二：直接提交文本

`ash
curl -X POST "http://localhost:8001/api/v1/rag/documents/text?title=考勤制度&content=公司实行弹性工作制..." \
  -H "Authorization: Bearer <token>"
`

### 自然语言检索

`ash
curl -X POST "http://localhost:8001/api/v1/rag/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '"{\"query\": \"加班政策是什么？\", \"top_k\": 5}"'
`

---

## 测试

`ash
pytest tests/ -v
`

---

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 系统管理员 | admin | admin123456 |

---

## 数据库迁移

`ash
# 创建新迁移
alembic revision --autogenerate -m "add new table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1

# 查看历史
alembic history
`

---

## 许可证

MIT License
