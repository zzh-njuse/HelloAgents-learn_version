# Spec 001：Self-host 最小平台骨架

状态：草案
日期：2026-07-08
阶段：1

## Goal

把当前仓库从 Python 包/demo 形态，扩展为一个可以 self-host 启动的最小 Web 平台。

本 spec 完成后，项目应拥有后端 API、前端入口、Docker Compose、数据库连接、本地文件存储、workspace 概念和基础可观测性。它不要求实现学习资料处理或智能问答，只要求平台形态成立。

## Context

阶段 0 已确认：

- 第一产品形态是开源 self-host。
- Postgres 是正式 self-host 路线的业务事实来源。
- Qdrant 是可重建向量索引。
- Redis 是任务、缓存和协调用辅助设施。
- SQLite 只作为 demo/dev/local-only 便利模式，不是正式 self-host 主路径。
- Neo4j 后置。
- `hello_agents/` 保持为 framework 层，未来产品代码放到 `apps/` 下。

阶段 1 是后续资料 ingestion、RAG、章节化学习和练习闭环的工程承载层。

## Constraints

- 不把产品业务代码混入 `hello_agents/`。
- 不把 API key、上传原始文档或敏感 agent 输入写入明文日志。
- 不在阶段 1 实现复杂鉴权；第一版允许单用户 self-host。
- 不实现资料上传、解析、分块或向量写入。
- 不引入 Neo4j 作为默认依赖。
- 不让前端第一屏变成聊天框；第一屏应是平台工作台。

## Done When

阶段 1 完成时：

- `docker compose up` 可以启动最小平台。
- 后端提供健康检查、配置检查和 workspace 最小 API。
- 前端能展示系统状态、workspace 列表，并能创建/进入 workspace。
- Postgres migration 可以创建首批表。
- Qdrant、Redis、本地 storage root 的连通性或配置状态可见。
- `README` 或部署文档说明 self-host 启动方式。
- 后端测试、前端构建和 Compose 配置检查有明确命令。

## 范围内

### 1. 仓库结构

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
    requirements.txt
  web/
    src/
      app/
      components/
      features/
      lib/
    package.json
docker-compose.yml
.env.example
storage/
```

说明：

- `hello_agents/` 继续作为可复用 agent framework。
- `apps/api/` 承载产品后端。
- `apps/web/` 承载产品前端。
- `storage/` 是 self-host 本地文件存储根目录，实际运行产物应被 `.gitignore` 排除。

### 2. 后端 API

最小 API 包括：

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/health` | 进程级健康检查，不访问外部依赖 |
| `GET` | `/ready` | 检查 Postgres、Qdrant、Redis、storage root 是否可用 |
| `GET` | `/api/v1/system/info` | 返回非敏感系统配置摘要 |
| `GET` | `/api/v1/workspaces` | 列出 workspace |
| `POST` | `/api/v1/workspaces` | 创建 workspace |
| `GET` | `/api/v1/workspaces/{workspace_id}` | 读取 workspace |

阶段 1 暂不提供删除 workspace。删除语义涉及数据级联和索引清理，应在后续 spec 中单独设计。

### 3. 数据库

阶段 1 只创建最小业务表：

```text
workspaces
  id
  name
  slug
  description
  created_at
  updated_at
```

要求：

- 使用 Postgres 作为正式 self-host 默认数据库。
- 使用 migration 管理 schema。
- 后续所有用户可见业务表应能直接或间接追溯到 workspace。
- 不在阶段 1 设计完整 document/chunk/course/exercise schema。

### 4. 本地文件存储

阶段 1 不实现上传，但应建立 storage root 配置和检查：

```text
STORAGE_ROOT=./storage
```

要求：

- 应能创建或检查 storage root。
- 不把运行时上传文件纳入 git。
- 后续阶段应在 Postgres 中保存文件元数据和路径引用。

### 5. Qdrant 与 Redis

阶段 1 只做连接和状态检查：

- Qdrant：检查服务是否可访问，不创建正式 collection。
- Redis：检查服务是否可访问，不实现后台 job。

这样可以让 self-host 拓扑提前成型，同时避免在资料管线前过早设计索引细节和任务系统。

### 6. 前端入口

前端第一屏应是平台工作台，而不是营销页或聊天页。

最小页面包括：

- 顶部或侧边平台导航。
- 系统状态区域：API、Postgres、Qdrant、Redis、storage。
- Workspace 列表。
- 创建 workspace 的表单或弹窗。
- 进入 workspace 后的空状态页面，为阶段 2 的资料入口预留位置。

页面文案应克制、工具化，避免把未实现能力包装成已完成能力。

### 7. Docker Compose

最小 Compose 服务：

```text
postgres
qdrant
redis
api
web
```

要求：

- 使用 `.env` 配置。
- Postgres、Qdrant、Redis 使用 named volumes。
- 本地文件存储使用仓库内 `storage/` 或可配置挂载目录。
- `web` 服务需要容器化；正式 self-host 验收不要求用户另开本地 dev server。
- Compose 文件不包含真实 API key。
- Neo4j 不进入阶段 1 Compose。

### 8. 基础可观测性

阶段 1 至少提供：

- 结构化日志或清晰的文本日志。
- request ID 或等价请求追踪字段。
- `/health` 与 `/ready`。
- 启动时输出非敏感配置摘要。

阶段 1 不需要实现完整 `agent_runs`、`tool_calls`、`cost_events`。

### 9. Review 记录

阶段 1 需要建立 `reviews/` 目录，用于保存 OCR/CR review 摘要。

要求：

- 每次有实质代码变更并运行 OCR review 后，应新增一条 review 记录。
- 记录应包含审查对象、背景、命令、结论、采纳项、拒绝项、后续动作和验证结果。
- OCR 结论是工程辅助，不是绝对命令；高置信问题优先修复，中低置信问题逐项判断。

## 范围外

- 用户登录、多用户权限和 OAuth。
- 文件上传和 ingestion job。
- PDF/Markdown/text 解析。
- embedding 计算和 Qdrant 写入。
- RAG 问答。
- Course Reader。
- agent run trace 和 token 成本统计。
- 生产级 HTTPS、域名、反向代理和云部署。

## 建议实现顺序

1. 创建阶段 1 app 目录和依赖文件。
2. 实现后端 settings、health、ready。
3. 引入数据库连接和 migration。
4. 创建 `workspaces` 表和 workspace API。
5. 创建前端 app shell、系统状态和 workspace 页面。
6. 编写 Dockerfile 和 `docker-compose.yml`。
7. 补充 `.env.example` 和 self-host 启动文档。
8. 跑测试、构建和 Compose 配置检查。
9. 对实质代码 diff 运行 OCR review，并把摘要存入 `reviews/`。

## 验证计划

后端：

```powershell
python -m pytest -q
```

阶段 1 后续可能增加更窄命令，例如：

```powershell
python -m pytest apps/api/tests -q
```

前端：

```powershell
npm install
npm run build
```

Compose：

```powershell
docker compose config
docker compose up --build
```

如果本机缺少 Docker 或 Node，应记录原因，并至少完成可运行代码路径的单元测试。

## 风险与处理

| 风险 | 处理方式 |
|---|---|
| 平台代码污染 framework 层 | 产品代码只放 `apps/`，只通过公开接口引用 `hello_agents/` |
| 一开始 schema 设计过大 | 阶段 1 只建 `workspaces`，document/chunk 后置 |
| Compose 成本过高 | Qdrant/Redis 只做状态检查，不提前实现复杂使用 |
| 前端变成展示页而不是工具 | 第一屏直接做 workspace 工作台 |
| 删除语义过早进入 | 阶段 1 不做删除 API |
| 技术栈选择拖延 | 通过阶段 1 ADR 先提出建议，人工确认后再实现 |

## 已确认事项

- 阶段 1 接受 FastAPI + SQLAlchemy + Alembic + React/Vite/TypeScript 作为实现栈。
- 前端包管理器使用 `npm`，优先降低 self-host 用户和面试演示的门槛。
- 依赖管理方式确认：framework 依赖继续在顶层 `pyproject.toml`；后端应用依赖放 `apps/api/requirements.txt`；前端应用依赖放 `apps/web/package.json`。
- 阶段 1 先不引入 worker，Redis 仅用于 ready check 和后续任务系统预留。
- 阶段 1 的前端需要容器化；`docker compose up` 应能带起 `web` 服务。
- 阶段 1 需要 `docs/02-stage-1-self-host-platform/reviews/` 下的 OCR/CR review 记录模板。

## 实现补充

- 阶段 1 可以保留前端本地 dev server 作为开发便利方式，但正式 self-host 验收以 Compose 中的 `web` 服务可启动为准。
