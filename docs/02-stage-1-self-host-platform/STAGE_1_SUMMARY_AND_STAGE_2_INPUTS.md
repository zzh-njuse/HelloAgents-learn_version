# 阶段 1 总结与阶段 2 输入

日期：2026-07-09

## 阶段 1 简短总结

阶段 1 已把项目从 Python 包 / demo 推进为可 self-host 启动的 Web 平台骨架。

本阶段实际完成：

- 新增 FastAPI 后端应用，提供 health、ready、system info 和 workspace API。
- 新增 SQLAlchemy model、Alembic migration，并以 Postgres 作为 self-host 权威业务库。
- 新增 React / Vite / TypeScript 前端入口，提供 workspace 列表、状态卡片、创建 workspace 表单和当前 workspace 面板。
- 新增 Docker Compose，启动 Postgres、Qdrant、Redis、API、Web。
- 新增本地文件存储目录约定和 self-host runbook。
- 完成 Codex self-review、OpenCodeReview 正式审查、修复和复验。

阶段 1 的产品边界：

- 当前是平台骨架，不是资料学习闭环。
- 可以创建和查看 workspace。
- 可以看到 API、Postgres、Qdrant、Redis、Storage 的 readiness 状态。
- 尚未接入资料上传、解析、RAG、章节化学习、练习和记忆。

## 验证结果

已通过：

- `python -m pytest -q`
- API focused tests：4 passed
- `npm.cmd run build`
- `npm.cmd audit`：0 vulnerabilities
- `docker compose config`
- `docker compose build api web`
- `docker compose up -d`
- `docker compose ps`
- `GET /ready`
- Web HTTP 200
- 通过 API 创建 workspace 的 compose smoke test

当前可访问入口：

- Web: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`

## 阶段 2 应继承的输入

阶段 2 的目标是资料驱动学习入口。开始设计前，需要显式继承阶段 1 的以下结果：

- 以 workspace 作为资料、文档版本、chunk、索引和后续学习资产的归属边界。
- Postgres 继续作为事实来源；Qdrant 只保存可重建向量索引。
- Redis 目前只作为 self-host 基础依赖和后续任务辅助预留，阶段 2 如需异步解析任务，需要重新写 spec / ADR。
- API / Web / DB / Qdrant / Redis 的 compose 启动链路已经存在，阶段 2 应在此基础上扩展，而不是另起一套 demo。

## 暂缓风险与后续 hardening

以下 OCR 建议在阶段 1 暂未采纳，但应作为后续输入：

- API / Web 容器非 root 用户：方向合理，但涉及 bind mount 权限、nginx 低端口绑定和跨平台 self-host 体验，后续应单独设计。
- Redis 密码：阶段 1 默认本地开发形态未启用认证。后续 deployment hardening 应设计 `REDIS_PASSWORD` 和对应连接串。
- Qdrant API key：阶段 1 默认本地开发形态未启用认证。后续需要评估 Qdrant 本地 auth 与 API 访问方式。
- 默认端口暴露策略：尝试绑定 `127.0.0.1` 在当前 Windows Docker Desktop 环境失败，后续应通过文档和部署配置说明防火墙/端口暴露策略。
- Qdrant healthcheck：镜像内置工具不确定，暂不加入 compose healthcheck。后续可单独验证跨平台可用写法。
- Postgres 容器集成测试：当前 API focused tests 使用 SQLite 以获得快速反馈；后续应增加真实 Postgres 测试层。

## 阶段 2 开发注意事项

- 资料上传、解析、chunk、embedding、Qdrant upsert 都必须从 spec 开始，不要直接把 RAG demo 代码塞进平台。
- 文档原文、解析结果、chunk metadata、处理状态、索引状态应先落 Postgres，再派生 Qdrant 索引。
- 删除资料、重建索引、重新解析文档版本必须有明确语义。
- 回答引用必须能追溯到 document / chunk / version，不能只返回模型自然语言。
- 如果引入后台任务或 worker，必须先写 ADR，明确 Redis 的角色、失败重试、幂等和可观测性。

## 协作流程经验

- Codex self-review 与 OCR 的分工是有效的：Codex 更适合范围和架构判断，OCR 更适合安全、部署和边界审计。
- OCR 不适合高频小步迭代。阶段 1 的正式 OCR 约使用 93.6 万 tokens，应作为阶段末质量门禁。
- 大 diff OCR 应先 preview，再用 `--audience agent --concurrency 4 --timeout 15 --background "<context>"`。
- OCR 超时后要检查残留进程，避免继续消耗 provider quota。
- 每阶段结束后都应生成本类总结文档，作为下一阶段 spec / ADR 的输入。
