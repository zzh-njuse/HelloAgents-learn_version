# AGENTS.md

## 仓库定位

- 将本仓库视为正在演进的 self-host 学习 Agent 平台，而不只是原始 HelloAgents demo。
- 保持 `hello_agents/` 框架层与未来 `apps/` 产品代码分离。
- 优先做小而可审查的变更。除非任务明确要求，否则不要把功能开发、大重构、格式化清理和文档重写混在一次变更里。
- 保留用户改动。不要回滚无关的 dirty files。

## 开发流程

- 非平凡任务应先在 `docs/<NN-stage-name>/specs/` 下创建或更新阶段内 spec。
- 架构决策应在 `docs/<NN-stage-name>/adr/` 下创建阶段内 ADR。
- 实现前先确认相关文件范围和预期验证命令。
- 代码实现后，先运行最窄的有意义测试；风险较高时再运行更宽的测试。
- Python 框架代码变更默认运行 `python -m pytest -q`，除非用户要求更窄检查。
- 文档-only 变更运行 `git diff --check`。
- 改变公开行为时，同一任务内同步更新文档和测试。

## Review 流程

- 结束前先自查 diff，重点看行为回归、缺失测试、数据丢失风险和意外扩大范围。
- 仅在用户要求 OCR/CR review，或用户批准真实 review 时使用 OpenCodeReview。安全预检命令是：
  - `C:\Users\Admin\bin\ocr.exe version`
  - `C:\Users\Admin\bin\ocr.exe review --preview`
  - `C:\Users\Admin\bin\ocr.exe -h`
- 真实 OCR review 使用 `C:\Users\Admin\bin\ocr.exe review --audience agent --background "<context>"`。
- OCR 结论是建议而不是绝对命令。修复高置信问题，完成测试验证，并说明被拒绝的建议。

## Self-Host 方向

- 默认产品目标是 self-host 部署：Docker Compose + Postgres + Qdrant + Redis + local file storage。
- Postgres 是正式 self-host 路线的事实来源。SQLite 只可作为 demo/dev/local-only 便利模式。
- Qdrant 是可重建向量索引，不是事实来源。
- 除非 spec 和 ADR 明确论证，不要把 Neo4j 引入默认运行依赖。
- 不要把 API key、上传原始文档或敏感 agent 输入写入明文日志。

## 文档资产

- 架构与蓝图：`docs/LEARNING_AGENT_BLUEPRINT.md`。
- 大阶段开发路线图：`docs/SELF_HOST_DEVELOPMENT_ROADMAP.md`。
- 数据库与部署计划：`docs/DATABASE_AND_DEPLOYMENT_PLAN.md`。
- 阶段 0 工作文档：`docs/01-stage-0-foundation/`。
- 后续阶段文档应放在 `docs/<NN-stage-name>/` 下，并按需使用 `specs/`、`adr/`、`evals/`、`reviews/` 子目录。
