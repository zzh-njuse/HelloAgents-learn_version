# 阶段 1 OCR/CR Review 记录

状态：模板
日期：2026-07-08

本目录用于保存阶段 1 的 OCR/CR review 摘要。每次有实质代码变更并运行 OpenCodeReview 或其他 code review 工具后，应新增一条记录。

建议文件名：

```text
YYYY-MM-DD-<short-topic>.md
```

## 记录模板

```markdown
# Review：<topic>

日期：YYYY-MM-DD
阶段：1
审查对象：<commit / diff / files>
审查工具：OpenCodeReview / manual CR / other

## 背景

本次变更解决什么问题，涉及哪些 spec/ADR。

## 命令

```powershell
<实际运行的 review 命令>
```

## 结论摘要

- High：
- Medium：
- Low：

## 采纳项

| 等级 | 问题 | 处理 |
|---|---|---|
| High/Medium/Low |  |  |

## 拒绝项

| 等级 | 问题 | 拒绝原因 |
|---|---|---|
| High/Medium/Low |  |  |

## 修复后验证

```powershell
<测试或检查命令>
```

结果：

## 后续动作

-
```

## 使用原则

- OCR/CR 结论是工程辅助，不是绝对命令。
- High 置信问题默认优先修复；如拒绝，必须写清原因。
- Medium 问题逐项判断。
- Low 问题不盲目修改，避免引入无关 churn。
- Review 记录应关注代码风险、测试缺口、数据安全和部署风险，不记录无关聊天内容。
