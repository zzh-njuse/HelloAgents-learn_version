# 阶段 1：Self-host 最小平台

状态：草案
日期：2026-07-08

本目录保存阶段 1 的工作文档。阶段 1 的目标是把项目从 Python 包/demo，推进为可以本地部署、可以打开网页、可以连接数据库和基础服务的 Web 平台。

## 阶段目标

阶段 1 解决的问题不是“学习 Agent 有多聪明”，而是“这个项目能不能像一个真实 self-host 应用一样跑起来”。

阶段完成后，用户应能：

- clone 仓库；
- 配置 `.env`；
- 使用 Docker Compose 启动 Postgres、Qdrant、Redis、后端 API 和前端；
- 打开浏览器看到一个可操作的平台入口；
- 创建或进入 workspace；
- 看到基础服务状态和本地存储配置。

## 当前文档

- Spec：`specs/001-self-host-platform-skeleton.md`
- ADR：`adr/001-stage-1-application-stack.md`
- OCR/CR review 记录模板：`reviews/README.md`

## 本阶段不做什么

- 不做资料上传与解析管线。
- 不做 RAG 问答。
- 不做章节生成、练习、记忆和个性化推荐。
- 不做多用户鉴权。
- 不引入 Neo4j。
- 不把 Chat 作为第一屏核心体验。

## 阶段完成标志

阶段 1 完成时应满足：

- 后端 API、前端入口、Postgres、Qdrant、Redis 和本地文件存储之间的关系清楚。
- `apps/api` 和 `apps/web` 与 `hello_agents/` 框架层边界清晰。
- 用户可以通过 self-host 流程启动项目。
- workspace 最小闭环可用。
- 文档、测试和部署说明能支持下一阶段资料管线开发。
