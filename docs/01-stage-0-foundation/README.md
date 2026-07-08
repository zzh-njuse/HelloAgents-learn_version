# 阶段 0：工程地基

状态：完成
日期：2026-07-08

本目录保存阶段 0 的工作文档。之后每个大阶段都使用独立目录，避免 spec、ADR、review 和 eval 资料散落在 `docs/` 顶层。

本文档以中文为人工审阅主版本，并保留少量英文术语，方便后续 agent 检索和执行。

## 目标

阶段 0 的目标是把项目从 demo 型代码库，整理成可以长期开发 self-host 产品的工程仓库。

这一阶段不以新增用户功能为主，而是建立后续阶段都要遵守的开发秩序、架构决策和验证习惯。

## 当前文档

- 阶段 0 spec：`specs/001-stage-0-foundation.md`
- self-host 数据栈 ADR：`adr/001-self-host-data-stack.md`

## 目录约定

后续阶段目录建议保持如下形态：

```text
docs/
  01-stage-0-foundation/
    README.md
    specs/
    adr/
    evals/
    reviews/
  02-stage-1-self-host-platform/
    README.md
    specs/
    adr/
    evals/
    reviews/
```

顶层文档只保留跨阶段战略材料：

- `docs/LEARNING_AGENT_BLUEPRINT.md`
- `docs/SELF_HOST_DEVELOPMENT_ROADMAP.md`
- `docs/DATABASE_AND_DEPLOYMENT_PLAN.md`
- `docs/AGENT_COLLABORATION_PLAYBOOK.md`

## 阶段完成标志

阶段 0 完成时应满足：

- `AGENTS.md` 中的仓库规则清晰可执行。
- self-host 数据栈决策已经记录为 ADR。
- Agent 协作开发流程已经文档化，并能从下一个任务开始使用。
- OCR/OpenCodeReview 已经配置到足以审查有意义的代码变更。
- 当前路线图、数据库计划和部署计划在产品方向上保持一致。
- 文档变更和 Python 代码变更的验证命令已经明确。

以上条件已于 2026-07-08 完成确认。
