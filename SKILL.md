---
name: git-diff
description: Git 修改总结工具 - 帮助 AI 理解和总结代码变更
version: 1.0.0
author: xiaohangxu
categories:
  - git
  - code-review
  - utility
---

# Git Diff 总结工具

## 🎯 核心职责

帮助 AI 理解和总结 Git 代码变更，支持两种主要场景：

1. **分支对比总结**：对比源分支和当前分支的所有修改
2. **指定范围总结**：选择特定 commit 范围进行 diff 分析

---

## 🚀 使用流程

### 场景一：总结当前分支修改（与源分支对比）

当用户想了解当前分支相对于源分支（如 main/master）的所有修改时：

```bash
# 1. 执行 summary 命令，结果自动保存到 .codebuddy/git-diff/ 目录
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py summary

# 2. 如果需要指定源分支
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py summary --source main

# 3. 指定输出文件
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py summary -o changes.md
```

**然后**：
1. 读取生成的 Markdown 文件
2. 分析 diff 内容，生成整体总结和文件变更详情
3. **重要：将总结内容追加写入到该 Markdown 文件末尾**

### 场景二：指定 Commit 范围总结

当用户想了解特定 commit 范围的修改时：

```bash
# 1. 首先列出 git log 供用户选择
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py log

# 2. 用户选择后，执行指定范围的 diff
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py diff --from <起始commit> --to <结束commit>

# 示例：从 abc1234 到 HEAD
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py diff --from abc1234

# 指定输出文件
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py diff --from abc1234 -o diff.md
```

**然后**：
1. 读取生成的 Markdown 文件
2. 分析 diff 内容，生成整体总结和文件变更详情
3. **重要：将总结内容追加写入到该 Markdown 文件末尾**

---

## ⚡ 核心执行原则

| 原则 | 说明 |
| --- | --- |
| **先获取 diff** | 必须先执行脚本获取 diff 信息，再进行总结 |
| **结构化总结** | 总结应包含：修改概述、影响范围、关键变更点 |
| **代码理解** | 分析代码变更的意图和潜在影响 |
| **写入文件** | **必须将总结内容追加写入到生成的 Markdown 文件末尾** |
| **交互式选择** | 使用 `log` 命令时，展示列表让用户选择 commit 范围 |

---

## 🔧 命令速查

| 命令 | 说明 |
| --- | --- |
| `summary` | 总结源分支到当前分支的修改，输出到文件 |
| `summary --source <branch>` | 指定源分支进行对比 |
| `summary -o <file>` | 指定输出文件路径 |
| `log` | 列出最近 20 条 commit |
| `log --limit <n>` | 列出最近 n 条 commit |
| `diff --from <commit>` | 从指定 commit 到 HEAD 的 diff |
| `diff --from <c1> --to <c2>` | 指定范围的 diff |
| `diff -o <file>` | 指定输出文件路径 |

**默认输出路径**: `.codebuddy/git-diff/<commit摘要>_<时间戳>.md`

例如：`.codebuddy/git-diff/feat_添加用户登录功能_20260203_143025.md`

---

## 📋 总结模板

执行完脚本获取 diff 后，按以下结构提供总结：

### 输出格式

**先输出整体总结，再按文件输出详细变更**

---

### 示例输出

#### 修改总结

增加问题分类 ID 支持，涉及请求参数、调用签名及结构体扩展等调整。

- 调整 CreateQA 请求中 AppId/PartnerId 参数来源为 req.AppId
- 导入 time 包并整理包顺序
- 新增提前获取问题分类 ID 逻辑，失败不影响主流程
- 修改 callQuestionStream 签名，增加 questionClassId 参数
- 修改 recordOnceQuestionStreamAsync 签名，增加 cachedQuestionClassId 参数
- 日志优先使用缓存分类 ID，减少重复调用
- 扩展 questionStreamAdapter 结构体，新增 questionClassId 字段
- 在最终流包附加问题分类 ID 并记录日志

#### 文件变更详情

| 文件路径 | 文件总结 |
| --- | --- |
| service/qarobot_go.go | 将 CreateQA 请求中的 AppId 和 PartnerId 参数改为使用 req.AppId 而非 appid |
| logic/MisiQarobotByHunYun/OnceQuestionStream.go | 导入 time 包并调整包顺序；新增提前获取问题分类ID逻辑，失败时不影响主流程；修改 callQuestionStream 签名，增加 questionClassId 参数；修改 recordOnceQuestionStreamAsync 签名，增加 cachedQuestionClassId 参数；记录日志时优先使用缓存分类ID，减少重复调用；扩展 questionStreamAdapter 结构体，新增 questionClassId 字段；在最终流包附加问题分类ID并记录日志 |

---

### 总结模板

```markdown
#### 修改总结

[一句话概括本次修改的核心目的]

- [变更点1]
- [变更点2]
- [变更点3]
- ...

#### 文件变更详情

| 文件路径 | 文件总结 |
| --- | --- |
| path/to/file1.go | [该文件的具体修改点，用分号分隔多个修改] |
| path/to/file2.go | [该文件的具体修改点] |
```

### 总结要求

1. **整体总结**：先用一句话概括修改目的，再用列表列出所有关键变更点
2. **文件详情**：按文件路径列表，每个文件总结其具体修改内容
3. **表达清晰**：使用技术术语准确描述，如"签名"、"参数"、"结构体"等
4. **逻辑分组**：相关的修改点放在一起描述

---

## 📚 关键资源

- **脚本工具**：`scripts/main.py` - 核心 diff 工具
- **使用指南**：`references/guide.md` - 详细使用说明
