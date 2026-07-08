# Spec 001：阶段 0 工程地基

状态：完成
日期：2026-07-08
阶段：0

## 目标

在正式实现 self-host Web 平台之前，先建立清晰、一致、可重复执行的工程地基。

本 spec 被接受后，后续开发不应再以临时 demo 修改为主要方式。每个有意义的任务都应从明确范围的 spec 或 ADR 开始，完成相应验证，并留下可审查的工程证据。

## 背景

本仓库最初是 HelloAgents 学习/demo 代码库。现在产品方向已经调整为：逐步演进成一个可以 self-host、可以真实部署、可以长期维护、也可以作为面试谈资的学习 Agent 平台。

当前战略文档包括：

- `docs/LEARNING_AGENT_BLUEPRINT.md`
- `docs/SELF_HOST_DEVELOPMENT_ROADMAP.md`
- `docs/DATABASE_AND_DEPLOYMENT_PLAN.md`
- `docs/AGENT_COLLABORATION_PLAYBOOK.md`

阶段 0 的任务是把这些文档转化为可执行的开发秩序。它的产出应该让阶段 1 可以放心开始平台骨架开发。

## 范围内

1. 仓库级开发规则
   - 维护 `AGENTS.md`，作为 agent 持久规则的简洁来源。
   - 明确阶段内 spec、ADR、eval 记录和 review 记录的存放位置。
   - 保持 `hello_agents/` 框架代码与未来 `apps/` 产品代码分离。

2. Self-host 架构决策
   - 在 `adr/001-self-host-data-stack.md` 中记录初始数据栈决策。
   - 将 Postgres 作为正式 self-host 路线的业务事实来源。
   - 将 Qdrant 视为可重建的向量索引。
   - 将 Redis 视为任务、缓存和协调用辅助设施，而不是权威存储。
   - Neo4j 暂不进入默认运行依赖，除非后续 ADR 明确论证。

3. Agent 协作开发流程
   - 默认采用：spec -> plan -> implementation -> focused tests -> self-review -> 必要时 OCR review -> fixes -> final verification -> retrospective update。
   - 对 schema、migration、deployment、删除逻辑、鉴权和成本敏感变更设置更强 gate。
   - 保留用户改动，避免夹带无关重构。

4. Review 与验证基线
   - 文档-only 变更运行 `git diff --check`。
   - Python 框架代码变更默认运行 `python -m pytest -q`，除非有明确理由只跑更窄测试。
   - 对有意义或高风险的代码变更，按需使用本地 OpenCodeReview。

5. 文档一致性
   - 让路线图、数据库/部署计划、协作 playbook 在方向上保持一致。
   - 对已知短板显式记录，不用文档掩盖真实风险。

## 范围外

- 构建 Web 后端或前端。
- 增加 Docker Compose 运行服务。
- 设计完整产品 schema。
- 实现上传、ingestion、RAG、章节生成、练习或记忆功能。
- 引入 hosted SaaS 作为第一产品形态。
- 引入 Neo4j、复杂 multi-agent 编排或自动化运营任务。

## 交付物

| 交付物 | 路径 | 状态 |
|---|---|---|
| 仓库规则 | `AGENTS.md` | 已建立 |
| 协作 playbook | `docs/AGENT_COLLABORATION_PLAYBOOK.md` | 已建立 |
| 大阶段路线图 | `docs/SELF_HOST_DEVELOPMENT_ROADMAP.md` | 已归档 |
| 数据库与部署计划 | `docs/DATABASE_AND_DEPLOYMENT_PLAN.md` | 已同步 |
| 阶段 0 spec | `docs/01-stage-0-foundation/specs/001-stage-0-foundation.md` | 已完成 |
| self-host 数据栈 ADR | `docs/01-stage-0-foundation/adr/001-self-host-data-stack.md` | 已接受 |
| OCR 项目规则 | `.opencodereview/rule.json` | 已配置 |

## 后续任务必须遵守的工作流

每个非平凡任务都应先说明：

```text
Goal: 本次任务解决什么问题
Context: 相关代码、文档和历史决策是什么
Constraints: 哪些边界、风险和架构约束必须遵守
Done when: 什么结果算完成
```

然后按如下链路推进：

```text
spec 或 ADR
-> Codex plan
-> implementation
-> focused verification
-> self-review
-> OCR/CR review when useful
-> fixes
-> final verification
-> human decision
-> retrospective update
```

小型文档变更可以跳过完整 spec，但仍需明确范围，并运行 `git diff --check`。

## 风险分级与 gate

| 等级 | 示例 | Agent 自主度 | 必要验证 |
|---|---|---|---|
| L0 | 解释、调研、计划 | 可自由分析 | 说明来源或假设 |
| L1 | 文档、测试、小修复 | 可直接编辑 | `git diff --check` 或 focused tests |
| L2 | 小功能、API 适配、存储适配 | 需要 spec | focused tests + self-review |
| L3 | schema、migration、删除逻辑、鉴权、部署 | 需要 spec 或 ADR，并有人类 gate | tests + OCR review + 明确接受 |
| L4 | 大范围重构、自动迁移、真实部署操作 | 不允许无审核自主推进 | 拆阶段、分批 review、人工批准 |

## 验收标准

阶段 0 满足以下条件后可以视为完成：

- `AGENTS.md` 准确反映当前仓库规则。
- 阶段内文档结构已经建立在 `docs/01-stage-0-foundation/` 下。
- self-host 数据栈 ADR 已被接受，或剩余问题被显式列出。
- 数据库/部署计划和大阶段路线图在 Postgres、SQLite、Qdrant、Redis、Neo4j 的定位上不再冲突。
- OCR 使用方式已经记录到足以后续审查代码 diff，不需要重新摸索工具流程。
- `git diff --check` 通过。
- 如果阶段 0 中发生代码变更，`python -m pytest -q` 通过，或失败原因被明确记录。

## 已确认事项

- 每个阶段保留自己的 `reviews/` 目录；暂不额外维护顶层 review 索引。
- 阶段 1 的后端技术栈不在阶段 0 决策，后续通过阶段 1 spec 或 ADR 讨论。
- 阶段 0 不创建 repo-local Codex skill；等后续任务中同一流程重复出现并跑顺后再沉淀。
- ADR 中偏具体实现的问题不阻塞阶段 0，统一延后到阶段 1 或对应功能阶段讨论。

## 阶段 0 完成记录

- 2026-07-08，人工确认本 spec 可以更新为 `完成`。
- 2026-07-08，人工确认 self-host 数据栈 ADR 可以更新为 `已接受`。
- 本次收尾任务负责完成最终 `git diff --check` 和 git 提交。
