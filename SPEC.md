# AI驱动的人力资源系统 · 项目规格说明书

## 1. 项目概述

- **项目名称**: AI驱动的人力资源系统（HelixHR - AI-Driven Human Resources System）
- **项目类型**: RESTful API 后端服务
- **核心功能**: 基于 FastAPI 构建的 AI 驱动型人力资源系统，支持 RBAC 权限控制、JWT 认证、MySQL 数据库存储，并集成 RAG（检索增强生成）模块。
- **目标用户**: 企业 HR 管理人员、行政人员、普通员工

## 2. 技术栈

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| Web 框架 | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0+ |
| 数据库迁移 | Alembic |
| 验证 | Pydantic v2 |
| 认证 | JWT (python-jose) + bcrypt (passlib) |
| 限流 | slowapi |
| 文档嵌入 | sentence-transformers（all-MiniLM-L6-v2）|
| 向量数据库 | ChromaDB |
| 容器化 | Docker + docker-compose |
| 测试 | pytest + pytest-asyncio |
| 日志 | loguru |
| 配置 | YAML 文件驱动（PyYAML）|

## 3. 数据模型规格

- **sys_user**: 用户表（username, email, hashed_password, full_name, is_active, is_superuser）
- **sys_role**: 角色表（name, code, permissions JSON, is_system）
- **sys_user_role**: 用户角色关联表
- **sys_department**: 部门表（name, code, parent_id 树形结构, manager_id）
- **sys_employee**: 员工表（employee_number 工号, department_id, position, employment_status）
- **sys_salary**: 薪资表（employee_id, base_salary, bonus, deductions, tax, net_salary）

## 4. API 端点

- POST /api/v1/auth/login - 登录
- GET /api/v1/auth/me - 当前用户
- POST /api/v1/employees/ - 创建员工
- GET /api/v1/employees/ - 员工列表
- GET /api/v1/employees/{id} - 员工详情
- PUT /api/v1/employees/{id} - 更新员工
- DELETE /api/v1/employees/{id} - 删除员工
- GET /api/v1/departments/ - 部门列表
- POST /api/v1/departments/ - 创建部门
- GET /api/v1/salaries/ - 薪资列表
- POST /api/v1/salaries/ - 录入薪资
- GET /api/v1/roles/ - 角色列表
- POST /api/v1/rag/query - RAG 检索
- POST /api/v1/rag/documents/upload - 上传文档
- GET /api/v1/rag/stats - RAG 统计

## 5. 验收标准

- [x] 所有 CRUD API 可正常调用
- [x] JWT 认证通过后可访问受保护接口
- [x] RBAC 权限控制正确拦截未授权请求
- [x] RAG 文档上传后可通过自然语言检索相关内容
- [x] Docker Compose 一键启动所有服务
- [x] pytest 单元测试覆盖核心业务逻辑
- [x] 配置通过 config.yaml 管理，无硬编码值
