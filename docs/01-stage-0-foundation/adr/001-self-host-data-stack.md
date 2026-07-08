# ADR 001：Self-host 数据栈

状态：已接受
日期：2026-07-08
阶段：0

## 背景

项目正在从 HelloAgents demo 代码库，演进为一个 self-host 学习 Agent 平台。

第一产品形态是开源 self-host 部署。理想使用方式是：用户 clone 仓库，配置环境变量，启动本地服务，然后在不依赖 hosted SaaS 后端的情况下使用平台。

当前仓库已经展示过几类存储能力：

- SQLite：当前 memory/demo 代码中使用。
- Qdrant：当前 RAG demo 中作为向量数据库使用。
- Neo4j：以可选图数据库能力出现。

这些都是有价值的框架示例，但不能自动成为产品数据架构。产品需要明确的事实来源、可解释的索引重建语义，以及 self-host 用户容易理解的部署形态。

## 决策

正式 self-host 数据栈如下：

| 组件 | 角色 | 权威性 |
|---|---|---|
| Postgres | 业务数据库和事实来源 | 权威 |
| 本地文件存储 | 上传原始文件和派生文件 | 文件字节权威，元数据由 Postgres 引用 |
| Qdrant | 向量检索索引 | 可重建派生索引 |
| Redis | 后台任务协调、缓存、锁、限流状态 | 非权威 |
| SQLite | demo/dev/local-only 便利模式 | 不是正式 self-host 主路径 |
| Neo4j | 未来可选知识图谱能力 | 不是默认依赖 |

Postgres 是以下产品实体的权威存储：

- workspace
- document 与 document version
- 文件元数据与 checksum
- parsed chunk
- ingestion job 与处理状态
- 未来的 course structure 与 chapter
- 未来的 exercise、attempt、feedback 与 memory record
- 未来的 eval 与 trace 元数据

本地文件存储负责保存较大的文件字节：

- 用户上传原始文件
- 必要时生成的提取文本、页面 artifact
- 必要时生成的导出文件

Postgres 保存这些文件的引用信息，例如路径、checksum、MIME type、大小和所属关系。

Qdrant 只保存检索所需的 embedding 和最小 payload，例如 workspace ID、document ID、document version ID、chunk ID 和 source location。若 Qdrant 数据丢失或不一致，系统应能从 Postgres 和本地文件存储重建。

Redis 可以支持后台任务和临时协调，但产品状态不能依赖 Redis 的持久性。

## 配置方向

阶段 1 应引入类似如下配置：

```text
DATABASE_URL=postgresql://...
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379/0
STORAGE_ROOT=./storage
```

SQLite 后续可以作为 demo/dev 模式提供，但不能削弱正式 self-host 设计，也不能成为文档中的生产路径。

## 删除与重建语义

删除应围绕权威存储定义：

1. 在 Postgres 中删除或标记删除产品记录。
2. 根据保留策略删除或垃圾回收本地文件字节。
3. 清理 Qdrant 中的向量。
4. 如果 Qdrant 清理失败，Postgres 中的权威删除状态仍然成立，索引可后续 reconciliation。

索引重建应是显式动作：

1. 从 Postgres 读取 document/chunk 状态。
2. 必要时从本地文件存储读取 artifact。
3. 重新计算 embedding。
4. 使用稳定的 Postgres ID 重建 Qdrant points。

## 影响

正向影响：

- Self-host 故事清晰，用户熟悉 Postgres + Docker Compose 的部署形态。
- Postgres 适合表达 workspace、document、job、course、exercise、memory、eval trace 等关系型业务数据。
- Qdrant 可以专注检索优化，不会变成隐藏事实来源。
- Redis 可以提升任务流体验，但不会制造数据丢失语义混乱。
- Neo4j 保留为未来知识图谱能力，不拖累第一版部署。

成本：

- 阶段 1 必须引入 migration 纪律。
- 正式 self-host 路线需要 Docker Compose。
- 数据库相关代码需要测试策略。
- 如果保留 SQLite 支持，必须把它当作兼容/便利模式，而不是设计中心。

## 备选方案

### SQLite 作为主 self-host 数据库

拒绝作为正式路径。SQLite 很适合 demo 和 local-only 工具，但计划中的平台需要后台任务、更丰富的并发访问、migration 纪律，以及未来向多用户演进的部署故事。

### Qdrant 作为主要 document store

拒绝。向量数据库适合做检索索引，不适合作为 document version、删除语义、用户数据、练习记录和审计 trace 的事实来源。

### Neo4j 作为默认依赖

早期拒绝。图数据库未来可能对 prerequisite graph 或 concept map 有价值，但在 ingestion 和学习闭环稳定之前，会明显提高部署成本。

### Hosted SaaS 优先

当前拒绝。项目现阶段目标是开源 self-host。Hosted 部署可以以后重新评估，但不应塑造第一版架构。

## 后续实现问题

以下问题偏向具体实现，不阻塞阶段 0 的数据栈方向确认。它们应在阶段 1 或对应功能阶段通过 spec/ADR 再决策。

- 阶段 1 是否使用 SQLAlchemy + Alembic，还是选择其他 Python 数据库/migration 栈？
- Qdrant 应该按 deployment、workspace 还是 embedding model 划分 collection？
- 阶段 1 的文件存储是否只做 local storage，还是从一开始就预留 S3-compatible storage 接口？
- 阶段 5 做成本和质量看板前，最小 trace schema 应该提前到什么时候引入？
