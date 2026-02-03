# Git Diff 总结工具使用指南

## 概述

Git Diff 总结工具帮助开发者快速了解代码变更，支持两种主要使用场景：

1. **分支对比**：查看当前分支相对于源分支（main/master）的所有修改
2. **范围选择**：指定特定 commit 范围进行 diff 分析

## 快速开始

### 安装要求

- Python 3.8+
- Git 已安装并配置

### 基本用法

```bash
# 查看帮助
python3 scripts/main.py --help

# 查看版本
python3 scripts/main.py --version
```

## 功能详解

### 功能一：分支对比总结 (summary)

对比源分支和当前分支之间的所有修改。

```bash
# 自动检测源分支（优先使用上游分支，回退到 main/master）
python3 scripts/main.py summary

# 指定源分支
python3 scripts/main.py summary --source main
python3 scripts/main.py summary -s develop
```

**输出内容：**
- 源分支和当前分支信息
- 共同祖先 commit
- Commit 列表
- 文件变更统计
- 详细 diff 内容

**源分支检测顺序：**
1. 命令行指定的 `--source` 参数
2. Git 上游分支 (`@{upstream}`)
3. `main` 分支
4. `master` 分支

### 功能二：Git Log 列表 (log)

列出最近的 commit 记录，方便选择 diff 范围。

```bash
# 列出最近 20 条 commit（默认）
python3 scripts/main.py log

# 列出最近 50 条 commit
python3 scripts/main.py log --limit 50
python3 scripts/main.py log -n 50
```

**输出格式：**
```
序号  Commit ID   日期         提交信息
1     abc1234     2026-02-03   feat: 添加新功能
2     def5678     2026-02-02   fix: 修复 bug
...
```

### 功能三：指定范围 Diff (diff)

对指定的 commit 范围进行 diff 分析。

```bash
# 从指定 commit 到 HEAD
python3 scripts/main.py diff --from abc1234
python3 scripts/main.py diff -f abc1234

# 指定完整范围
python3 scripts/main.py diff --from abc1234 --to def5678
python3 scripts/main.py diff -f abc1234 -t def5678
```

**参数说明：**
| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--from`, `-f` | 是 | - | 起始 commit（不包含） |
| `--to`, `-t` | 否 | HEAD | 结束 commit（包含） |

## 典型工作流

### 工作流 1：Code Review 准备

```bash
# 1. 查看当前分支相对于 main 的所有修改
python3 scripts/main.py summary --source main

# 2. 根据输出准备 code review 材料
```

### 工作流 2：版本发布总结

```bash
# 1. 查看最近的 commit
python3 scripts/main.py log --limit 30

# 2. 找到上个版本的 tag 或 commit，执行 diff
python3 scripts/main.py diff --from v1.0.0 --to v1.1.0
```

### 工作流 3：调查特定时间段的修改

```bash
# 1. 列出 commit 找到时间范围
python3 scripts/main.py log --limit 50

# 2. 选择起止 commit 进行 diff
python3 scripts/main.py diff --from abc1234 --to def5678
```

## 命令速查表

| 命令 | 说明 |
| --- | --- |
| `summary` | 总结源分支到当前分支的修改 |
| `summary --source <branch>` | 指定源分支 |
| `log` | 列出最近 commit |
| `log --limit <n>` | 指定显示数量 |
| `diff --from <commit>` | 从指定 commit 到 HEAD |
| `diff --from <c1> --to <c2>` | 指定范围 diff |

## 常见问题

### Q1: 无法确定源分支怎么办？

**答**：使用 `--source` 参数明确指定：
```bash
python3 scripts/main.py summary --source main
```

### Q2: commit ID 可以用缩写吗？

**答**：可以，Git 支持使用缩写的 commit hash，只要能唯一标识即可（通常 7 位以上）。

### Q3: 可以用 tag 名代替 commit ID 吗？

**答**：可以，任何 Git 可解析的引用都支持，包括：
- Commit hash (完整或缩写)
- 分支名
- Tag 名
- HEAD~n 等相对引用

### Q4: diff 输出太长怎么办？

**答**：可以将输出重定向到文件：
```bash
python3 scripts/main.py diff --from abc1234 > changes.diff
```

## 更新日志

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| 1.0.0 | 2026-02-03 | 初始版本，支持 summary/log/diff 命令 |
