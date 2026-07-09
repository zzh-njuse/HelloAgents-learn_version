# AGENTS.md

## 阶段门禁与交接

- 阶段性开发必须保留人工确认 gate。实现、测试、OCR、修复可以由 agent 推进，但 commit 前应停在人工确认点，除非用户明确要求直接提交。
- 每个阶段收尾时，在 `docs/<NN-stage-name>/` 下新增或更新一个阶段总结与下一阶段输入文档。文档应简短记录：本阶段实际完成内容、验证结果、暂缓风险、下一阶段输入、协作流程经验。
- 下一阶段开始写 spec / ADR 前，应先读取上一阶段的总结与输入文档，避免把已知暂缓项丢在聊天记录里。
- 阶段末 review 记录必须进入 `docs/<NN-stage-name>/reviews/`。记录至少包括 review 背景、命令、审查范围、采纳项、暂不采纳项、复验命令和结果。

## 阶段启动 Checklist

- 开始新阶段的 spec / ADR 前，先读取这些文档：
  - 总路线：`docs/SELF_HOST_DEVELOPMENT_ROADMAP.md`
  - 上一阶段总结与输入：`docs/<previous-stage>/STAGE_*_SUMMARY_AND_STAGE_*_INPUTS.md`
  - 数据库与部署基线：`docs/DATABASE_AND_DEPLOYMENT_PLAN.md`
  - 协作流程：`docs/AGENT_COLLABORATION_PLAYBOOK.md`
  - 当前阶段已有的 `README.md`、`specs/`、`adr/`、`reviews/`
- 若当前阶段目录不存在，先创建 `docs/<NN-stage-name>/`，并按需保留 `specs/`、`adr/`、`evals/`、`reviews/` 子目录。
- 阶段入口 spec 应先说明：目标、非目标、用户故事、关键流程、接口草案、数据模型草案、失败模式、验收标准、验证命令和明确不做的内容。
- 遇到技术栈、数据 schema、迁移、任务队列、部署、安全边界、删除语义、成本策略、评测口径等不可逆或跨模块决策时，必须写 ADR。
- spec / ADR 应先交给用户核查和确认。确认后再进入开发计划和实现，不要让实现反向定义需求。
- 如果上一阶段总结里有暂缓风险或 hardening backlog，本阶段 spec 必须明确处理、继续暂缓，或说明为什么不相关。

## OCR 与独立审查

- 小改动不默认跑真实 OCR。小改动优先使用 Codex self-review + focused tests；阶段末、较大 diff、部署/安全相关变更再运行 OCR。
- OCR 标准流程：先运行 `git status --short`、`git diff --stat` 或 `git diff --cached --stat`、`ocr llm test`、`ocr review --preview`，再按需运行真实 review。
- 大 diff 的 OCR 推荐使用：`ocr review --audience agent --concurrency 4 --timeout 15 --background "<context>"`。
- 如果真实 OCR review 的 shell 命令超时，要检查是否残留 `ocr` 进程，必要时停止，避免继续消耗 provider quota。
- OCR finding 是独立建议，不是绝对命令。按采纳 / 暂不采纳分类处理；暂不采纳项必须写明原因，并进入后续阶段输入。
- Codex self-review 更适合阶段目标、架构边界、依赖边界和范围控制；OCR 更适合安全暴露、输入边界、容器健康检查、部署配置和测试缺口。两者互补，不互相替代。
- 真实 OCR review 成本可能很高。阶段 1 的 OCR 约使用 93.6 万 tokens，因此 OCR 更适合作为阶段末质量门禁，而不是高频小步迭代工具。

## Self-host 验证门槛

- 只要改动涉及 self-host 平台启动链路，最低验证应包括：`docker compose config`、`docker compose build api web`、`docker compose up -d`、`docker compose ps`、`/ready`、Web HTTP 200，以及至少一个业务 API smoke test。
- API 不应泄露部署细节。公开或半公开系统接口不要返回数据库 URL、Qdrant URL、本地文件路径、API key 或其他敏感连接信息。
- 继续保持应用依赖边界：顶层 `pyproject.toml` 管 framework 包；`apps/api/requirements.txt` 管后端应用；`apps/web/package.json` / `package-lock.json` 管前端；Docker 前端构建使用 `npm ci`。

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
