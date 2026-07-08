# ADR 001：阶段 1 应用技术栈与仓库布局

状态：已接受
日期：2026-07-08
阶段：1

## 背景

阶段 1 要把项目从 Python package/demo 变成可以 self-host 启动的 Web 平台。当前仓库的核心是 `hello_agents/` framework 层，尚无产品级 `apps/api`、`apps/web`、Docker Compose 和平台数据库 migration。

阶段 0 已确认：

- Postgres 是正式 self-host 事实来源。
- Qdrant 是可重建向量索引。
- Redis 是辅助设施。
- SQLite 不是正式 self-host 主路径。
- Neo4j 后置。
- 产品代码应与 `hello_agents/` framework 层分离。

因此阶段 1 需要选择一个足够稳妥、面试中也容易讲清楚的应用技术栈。

## 决策

阶段 1 采用以下技术栈：

| 层 | 决策 | 理由 |
|---|---|---|
| 后端框架 | FastAPI | Python 生态成熟，适合 API-first，自带 OpenAPI，和 agent/RAG Python 代码集成自然 |
| 数据访问 | SQLAlchemy 2.x sync engine | 成熟、可迁移、学习和调试成本低；阶段 1 不需要 async DB 复杂度 |
| Migration | Alembic | SQLAlchemy 标准迁移方案，适合 Postgres schema 演进 |
| Postgres driver | psycopg 3 | 现代 Postgres driver，配合 SQLAlchemy 使用 |
| 配置 | Pydantic Settings | 与现有 Pydantic 依赖一致，适合 `.env` 和环境变量 |
| 后端测试 | pytest + FastAPI TestClient/httpx | 贴合现有 pytest 基线，便于后续 API contract test |
| 前端 | Vite + React + TypeScript | 轻量、启动快、适合工具型 single-page app |
| 前端图标 | lucide-react | 轻量且符合工具型 UI 的图标需求 |
| 前端样式 | 普通 CSS 或 CSS Modules | 阶段 1 避免引入重型 UI 框架，先建立清晰信息架构 |
| 容器编排 | Docker Compose | self-host 用户熟悉，能同时管理 Postgres、Qdrant、Redis、api、web |

已确认：

- 使用上述建议技术栈。
- 前端包管理器使用 `npm`。
- 阶段 1 不引入 worker，Redis 只做 ready check 和后续任务系统预留。
- 阶段 1 前端需要容器化；`docker compose up` 应能带起 `web` 服务。
- 阶段 1 需要建立 OCR/CR review 记录模板。

## 仓库布局

建议新增：

```text
apps/
  api/
    learn_agent_api/
      main.py
      settings.py
      db/
      routers/
      services/
      schemas/
      observability/
    tests/
    alembic/
    requirements.txt
  web/
    src/
      app/
      components/
      features/
      lib/
    package.json
    vite.config.ts
docker-compose.yml
```

顶层 `pyproject.toml` 暂时继续代表 `hello_agents` framework 包，不直接塞入 FastAPI、SQLAlchemy、Alembic 等产品应用依赖。

阶段 1 后端依赖先放在 `apps/api/requirements.txt`，避免扩大 framework 包的安装体积。后续如果项目转成更正式的 monorepo，再考虑 Python workspace 或多个 package。

## 依赖管理边界

这条决策的含义是：

- 顶层 `pyproject.toml` 仍然描述 `hello_agents` 这个可复用 Python framework 包。
- `hello_agents` 的安装者不应因为只想使用 agent framework，就被迫安装 FastAPI、SQLAlchemy、Alembic、psycopg、uvicorn 等 Web 产品依赖。
- 阶段 1 的后端应用依赖放到 `apps/api/requirements.txt`。
- 阶段 1 的前端依赖放到 `apps/web/package.json`，并使用 `npm`。
- Docker Compose 构建 `api` 和 `web` 时分别读取各自 app 的依赖文件。

这种方式牺牲了一点 monorepo 一体化管理体验，但能保持 framework 层和 product app 层边界清晰。等项目形态稳定后，可以再通过新的 ADR 评估是否迁移到更统一的 workspace 管理方式。

## 后端同步/异步选择

阶段 1 后端数据库访问使用 SQLAlchemy sync engine。

理由：

- workspace CRUD 和 health check 不需要 async DB 的复杂度。
- sync SQLAlchemy + FastAPI 对初期测试和调试更直接。
- 后续真正需要高并发 ingestion job 或后台任务时，可以在任务系统层引入异步或 worker，而不是过早让所有 API 复杂化。

## 前端定位

阶段 1 前端是工具型平台工作台，不是 landing page。

第一屏应展示：

- 系统状态；
- workspace 列表；
- 创建 workspace；
- 当前 workspace 的空状态入口。

阶段 1 不做 Chat-first UI。聊天入口最多作为后续阶段能力预留，不作为当前产品中心。

## Docker Compose 形态

阶段 1 Compose 至少包含：

```text
postgres
qdrant
redis
api
web
```

`web` 服务应在容器内构建和运行前端。开发时可以额外使用本地 dev server，但不作为正式 self-host 验收路径。

不包含：

- Neo4j；
- worker；
- reverse proxy；
- HTTPS；
- hosted SaaS 依赖。

这些能力在后续阶段按 spec/ADR 引入。

## 影响

正向影响：

- 技术栈清晰、常见、面试中容易解释。
- 后端沿用 Python，便于复用 `hello_agents` framework。
- 数据库 migration 从阶段 1 开始建立纪律。
- 前端是轻量 SPA，足以承载 workspace 和后续 Course Reader。
- Docker Compose 直接对应 self-host 产品形态。

成本：

- 仓库会从纯 Python package 变成包含 Python app、Node app 和 Docker 的多组件项目。
- CI/测试命令会变多。
- 前端依赖需要 Node 环境。
- `apps/api/requirements.txt` 与顶层 `pyproject.toml` 之间需要维护清晰边界。

## 备选方案

### Flask

拒绝。Flask 足够轻，但阶段 1 需要 OpenAPI、类型化 request/response 和较清晰的 API contract，FastAPI 更合适。

### Django

暂不采用。Django 对后台管理和全栈应用很强，但本项目核心是 API-first、agent/RAG 管线和自定义前端体验。Django 的整体框架重量对阶段 1 偏高。

### FastAPI + async SQLAlchemy

暂不采用。它有长期价值，但阶段 1 的数据库访问很简单，async 会提高 migration、session 管理和测试复杂度。

### Next.js

暂不采用。阶段 1 不需要 SSR、路由数据加载和服务端渲染能力。Vite + React 更轻，self-host 容器也更容易解释。

### 只做后端，不做前端

拒绝。阶段 1 的目标是项目从“库”变成“应用”。没有前端入口，就仍然像 API demo，而不是可演示的学习平台。

### SQLite 优先

拒绝作为阶段 1 主路径。阶段 0 已确认 Postgres 是正式 self-host 事实来源。SQLite 后续可以作为 demo/dev 便利模式，但不能作为阶段 1 默认方向。

## 已确认事项

- 采用 FastAPI + SQLAlchemy + Alembic + Vite/React/TypeScript。
- 使用 `npm` 作为阶段 1 前端包管理器。
- 阶段 1 不引入 worker，Redis 仅用于 ready check 和任务系统预留。
- 阶段 1 接受 `apps/api/requirements.txt` 作为 app 依赖管理方式，不立刻改造顶层 `pyproject.toml`。
- 依赖边界正式确认：framework 依赖继续在顶层 `pyproject.toml`；后端应用依赖放 `apps/api/requirements.txt`；前端应用依赖放 `apps/web/package.json`。
- 前端容器化是阶段 1 self-host 验收要求；本地 dev server 只作为开发便利方式。
