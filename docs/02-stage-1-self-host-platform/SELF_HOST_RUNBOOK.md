# 阶段 1 Self-host 运行说明

状态：草案
日期：2026-07-08

本文档说明阶段 1 最小平台如何在本机启动。当前平台只包含基础工作台、workspace、服务状态检查和本地存储配置，不包含资料上传、RAG、章节或练习。

## 前置条件

- Docker Desktop 或兼容的 Docker Compose。
- 可用端口：`5432`、`6333`、`6379`、`8000`、`8080`。

## 启动

复制环境变量文件：

```powershell
Copy-Item .env.example .env
```

启动服务：

```powershell
docker compose up --build
```

访问：

```text
Web: http://localhost:8080
API: http://localhost:8000
API docs: http://localhost:8000/docs
```

## 健康检查

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

`/health` 只检查 API 进程。`/ready` 会检查 Postgres、Qdrant、Redis 和本地 storage。

## 数据库迁移

API 容器启动时会执行：

```powershell
alembic upgrade head
```

阶段 1 首个 migration 只创建 `workspaces` 表。

## 本地开发

后端应用依赖位于：

```text
apps/api/requirements.txt
```

前端应用依赖位于：

```text
apps/web/package.json
```

前端使用 `npm`。本地 dev server 可以作为开发便利方式，但阶段 1 的正式 self-host 验收以 `docker compose up` 中的 `web` 服务为准。

## 当前边界

- 不包含文件上传。
- 不包含 RAG。
- 不包含 worker。
- 不包含 Neo4j。
- 不包含多用户鉴权。
