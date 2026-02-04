# git-diff

> Git 修改总结工具 - 帮助 AI 理解和总结代码变更

## 📖 目录

- [快速开始](#-快速开始)
- [IDE 命令使用](#-ide-命令使用)
- [功能介绍](#-功能介绍)
- [使用指南](#-使用指南)
- [目录结构](#-目录结构)

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Git 已安装

### 使用方式

```bash
# 查看帮助
python3 scripts/main.py --help

# 功能1: 总结源分支到当前分支的修改
python3 scripts/main.py summary

# 功能2: 列出 git log 供选择
python3 scripts/main.py log

# 功能2: 指定范围 diff
python3 scripts/main.py diff --from <commit>

# 功能3: 合并 Review（分析最近一次 merge）
python3 scripts/main.py merge-review
```

## 💻 IDE 命令使用

### 安装命令到 CodeBuddy

将 `cmd/` 目录下的命令文件复制到 CodeBuddy 的用户命令目录：

```bash
# macOS / Linux
cp cmd/*.md ~/.codebuddy/commands/

# Windows
copy cmd\*.md %USERPROFILE%\.codebuddy\commands\
```

复制后重启 CodeBuddy 或刷新命令列表即可使用。

### 可用命令

| 命令 | 说明 | 文件 |
| --- | --- | --- |
| `/gitDiffSummary` | 总结当前分支相对于源分支的修改 | `cmd/gitDiffSummary.md` |
| `/gitMergeReview` | 分析最近一次 merge 的冲突和风险 | `cmd/gitMergeReview.md` |

### 使用示例

```
# 总结当前分支修改（自动识别源分支）
/gitDiffSummary

# 指定源分支
/gitDiffSummary main
/gitDiffSummary master

# 分析最近一次 merge
/gitMergeReview

# 分析指定的 merge commit
/gitMergeReview abc1234
```

### 输出示例

```markdown
# Git 修改总结

> 生成时间: 2026-02-03 16:12:48

## 基本信息

| 项目 | 值 |
| --- | --- |
| 源分支 | `origin/master` |
| 当前分支 | `feature/oneQuesWithClassId` |
| 共同祖先 | `5f1da565` |

## Commit 列表

​```
3da7665 Merge branch 'master' into feature/oneQuesWithClassId
691471f feature:增加问题分类ID
​```

## 文件变更统计

​```
 entity/proto/qarobot.proto                      |   3 +
 go.mod                                          |   4 +-
 go.sum                                          |   4 +-
 logic/MisiQarobotByHunYun/OnceQuestionStream.go | 101 ++++++++++++++++--------
 service/qarobot_go.go                           |   4 +-
 5 files changed, 76 insertions(+), 40 deletions(-)
​```

---

#### 修改总结

为 OnceQuestionStream 接口增加问题分类 ID（questionClassId）支持，优化调用流程并减少重复请求。

- 新增 proto 字段：请求增加 `needQuestionClassId`，响应增加 `questionClassId`
- 修复 CreateQA 请求参数：将 AppId/PartnerId 改为使用 `req.AppId`
- 新增提前获取问题分类 ID 逻辑：在调用流式问答前预获取，失败不影响主流程
- 优化 `callQuestionStream` 签名：增加 `questionClassId` 参数传递
- 优化 `recordOnceQuestionStreamAsync` 签名：增加 `cachedQuestionClassId` 参数
- 扩展 `questionStreamAdapter` 结构体：新增 `questionClassId` 字段缓存分类 ID
- 在最终流包附加问题分类 ID：当 `Finish=true` 且有分类 ID 时附加到响应
- 依赖更新：升级 qarobotgo 到 v1.1.94，新增 knowledge_guide_server 依赖

#### 文件变更详情

| 文件路径 | 文件总结 |
| --- | --- |
| entity/proto/qarobot.proto | 新增 `needQuestionClassId` 请求字段和 `questionClassId` 响应字段 |
| go.mod | 升级 qarobotgo v1.1.93→v1.1.94；新增 knowledge_guide_server v1.0.26 依赖 |
| go.sum | 同步更新依赖校验和 |
| logic/.../OnceQuestionStream.go | 导入 time 包；新增提前获取分类 ID 逻辑；修改函数签名；扩展结构体 |
| service/qarobot_go.go | 将 CreateQA 请求中 AppId/PartnerId 参数改为使用 req.AppId |
```

## 🎯 功能介绍

### 功能一：分支对比总结

对比源分支（main/master）和当前分支之间的所有修改：

```bash
python3 scripts/main.py summary
python3 scripts/main.py summary --source main
```

### 功能二：指定范围总结

1. 先列出 commit 记录：
```bash
python3 scripts/main.py log
python3 scripts/main.py log --limit 50
```

2. 选择范围进行 diff：
```bash
python3 scripts/main.py diff --from abc1234
python3 scripts/main.py diff --from abc1234 --to def5678
```

### 功能三：合并 Review

分析最近一次 merge commit 的详细情况，检查冲突解决和潜在风险：

```bash
# 分析最近一次 merge
python3 scripts/main.py merge-review

# 分析指定 merge commit
python3 scripts/main.py merge-review --commit abc1234
```

**输出内容：**
- 合并基本信息（merge commit、两个 parent、merge base）
- 冲突分析（哪些文件两边都有修改）
- 风险提示（被丢弃的代码、需要检查的手动合并）
- 各分支的修改统计
- 详细 diff 供 AI 分析

## 💡 使用指南

详细使用说明请参考 [使用指南](references/guide.md)。

## 📁 目录结构

```
git-diff/
├── SKILL.md          # Skill 入口文档
├── README.md         # 详细说明
├── cmd/              # IDE 命令（复制到 ~/.codebuddy/commands/）
│   ├── gitDiffSummary.md   # /gitDiffSummary 命令
│   └── gitMergeReview.md   # /gitMergeReview 命令
├── scripts/          # 脚本工具
│   └── main.py       # 主脚本
├── references/       # 参考文档
│   └── guide.md      # 使用指南
├── assets/           # 资源文件
│   └── templates/    # 文档模板
└── examples/         # 示例
```

## 📝 版本历史

| 版本  | 日期       | 主要变更     |
| ----- | ---------- | ------------ |
| 1.1.0 | 2026-02-04 | 新增 merge-review 命令，支持合并分析 |
| 1.0.0 | 2026-02-03 | 初始版本，支持 summary/log/diff 命令 |

## 📄 许可证

MIT License

---

Created by xiaohangxu
