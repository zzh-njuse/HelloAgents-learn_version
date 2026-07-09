# Review: 阶段 1 self-host platform skeleton

日期：2026-07-09
阶段：1
审查对象：当前 staged + unstaged diff
审查工具：Codex self-review、OpenCodeReview（DeepSeek provider）

## 背景

本次变更实现阶段 1 最小平台骨架：FastAPI 后端、workspace API、Postgres migration、React/Vite 前端工作台、Docker Compose、环境变量示例和 self-host 运行说明。

## OCR 命令

```powershell
ocr llm test
ocr review --preview
ocr review --audience agent --concurrency 4 --timeout 15 --background "Stage 1 self-host platform skeleton: FastAPI API with workspace CRUD and readiness checks, SQLAlchemy/Alembic/Postgres, React/Vite web entry, Docker Compose with Postgres/Qdrant/Redis/API/Web, local storage and self-host runbook."
```

## OCR 结果摘要

- OCR 正式审查成功，DeepSeek provider 连接正常。
- 审查范围：40 个变更文件，其中 34 个进入 review，6 个因扩展名规则排除。
- OCR 输出：42 条评论，约 935955 tokens，耗时 7 分 8 秒。
- 首次真实 review 因 shell 超时留下 `ocr` 进程，已停止后用更低并发和更长 OCR 超时重跑成功。

## 采纳项

- 移除 Alembic 配置中的硬编码数据库账号，避免示例配置看起来像真实凭据。
- 移除 `workspaces.slug` 的重复非唯一索引，保留唯一约束产生的索引。
- `/api/v1/system/info` 不再返回 Qdrant URL 和本地 storage path，只返回是否已配置。
- `/ready` 不再返回本地 storage path。
- Qdrant ready check 限制为 `http` / `https` URL，避免 `file://` 等非预期 scheme。
- 请求 ID header 做 trim 和长度限制，降低日志污染风险。
- workspace name/slug 增加非空白字符校验。
- workspace list 增加 `skip` / `limit` 分页参数。
- workspace detail 的 path 参数增加长度限制。
- 增加重复 workspace 名称和非法名称测试。
- API Dockerfile 增加 healthcheck。
- Web Dockerfile 使用 `npm ci`，并增加 healthcheck。
- Redis 增加 Compose healthcheck，API 等待 Redis healthy 后启动。
- 前端增加按钮/导航 focus-visible 样式，修正非标准 `font-weight: 720`。
- 前端拆分加载错误和表单错误，并补齐 workspace 名称长度校验。
- 前端 mount 时请求增加 AbortController，避免卸载后的异步状态更新。

## 暂不采纳项

- API / Web 容器非 root 用户：这是合理安全建议，但会牵涉 bind mount 权限、nginx 低端口绑定和跨平台 self-host 体验，阶段 1 暂不调整。
- Redis 密码、Qdrant API key：阶段 1 默认本地开发形态暂不启用认证，后续需要作为 deployment hardening 单独设计。
- Qdrant healthcheck：Qdrant 镜像内置工具不确定，避免引入一个可能在不同平台上不稳定的健康检查。
- 端口默认绑定 `127.0.0.1`：尝试后在当前 Windows Docker Desktop 环境中 `127.0.0.1:5432` 绑定失败，已回退。后续应通过部署文档说明防火墙/端口暴露策略。
- Alembic migration try/except 包装：收益主要是日志友好，当前不是功能或安全风险，暂缓。
- 将 SQLAlchemy engine 改为 lazy init：OCR 判断“import 即连接数据库”不准确，`create_engine` 不会立即建立连接，当前暂不改。
- 为 SQLite 单测增加 Postgres 容器测试：方向正确，但更适合作为阶段 1 后续 CI 增强。

## 修复后验证

```powershell
git diff --check
git diff --cached --check
python -m compileall -q apps\api
$env:PYTHONPATH='apps\api'; .tmp\api_venv\Scripts\python.exe -m pytest apps\api\tests -q
npm.cmd run build
npm.cmd audit
docker compose config
docker compose build api web
docker compose up -d
docker compose ps
Invoke-RestMethod http://localhost:8000/ready
Invoke-WebRequest -UseBasicParsing http://localhost:8080
```

结果：

- diff check 通过。
- Python 编译检查通过。
- API focused tests 通过：4 passed。
- 前端 production build 通过。
- npm audit：0 vulnerabilities。
- Docker Compose 配置检查通过。
- API/Web 镜像 build 通过。
- Docker Compose 启动通过。
- Postgres、Redis、API、Web healthy；Qdrant running。
- `/ready` 返回 ready，Web 返回 HTTP 200。
- 通过 API 创建了 `Stage 1 OCR Smoke` workspace 作为 compose 烟测。

## 与 Codex self-review 的差异

- Codex self-review 更擅长按阶段目标判断范围和取舍，先修了依赖边界、Vite 安全版本、Stage 1 不提前引入 Qdrant client 等问题。
- OCR 更像独立审计员，明显更关注安全暴露、输入边界、健康检查、容器配置和测试缺口。
- OCR 输出量很大，本次约 93.6 万 tokens；适合阶段末质量门禁，不适合每个小改动都全量运行。
- 后续更好的用法是：小改动用 Codex self-review + focused tests；阶段性较大 diff 再运行 OCR，并用 preview 控制范围。
