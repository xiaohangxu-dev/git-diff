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

**先输出整体总结，再按文件输出详细变更，最后列出风险提示和待确认事项**

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
| entity/proto/qarobot.proto | 新增 `needQuestionClassId` 请求字段和 `questionClassId` 响应字段 |
| go.mod | 升级 qarobotgo v1.1.93→v1.1.94；新增 knowledge_guide_server v1.0.26 依赖 |
| service/qarobot_go.go | 将 CreateQA 请求中的 AppId 和 PartnerId 参数改为使用 req.AppId 而非 appid |
| logic/.../OnceQuestionStream.go | 导入 time 包；新增提前获取问题分类ID逻辑；修改函数签名；扩展结构体 |

#### 风险提示

| 风险等级 | 风险描述 | 影响范围 | 建议 |
| --- | --- | --- | --- |
| ⚠️ 中 | Proto 新增字段需确认上下游兼容性 | `OnceQuestionStreamReq`、`OnceReplyStreamMeta` | 确认调用方是否已更新 proto 定义 |
| ⚠️ 中 | 依赖版本升级 qarobotgo v1.1.93→v1.1.94 | 整体服务 | 检查 changelog 确认无 breaking change |
| 🔴 高 | AppId 参数来源变更可能影响现有逻辑 | `CreateQA` 请求 | 确认 `req.AppId` 与原 `appid` 变量值一致 |

#### 待确认事项

| 序号 | 事项 | 原因 | 负责人 |
| --- | --- | --- | --- |
| 1 | `needQuestionClassId` 字段默认值行为 | 新增 bool 字段默认 false，老客户端不传时不会获取分类 ID | - |
| 2 | `QuestionTagsOnlyClass` 接口超时配置 | 新增的前置调用可能增加整体耗时 | - |
| 3 | 分类 ID 获取失败时的降级策略是否符合预期 | 当前策略为打日志继续，不影响主流程 | - |

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

#### 风险提示

| 风险等级 | 风险描述 | 影响范围 | 建议 |
| --- | --- | --- | --- |
| 🔴 高 | [严重风险，可能导致线上问题] | [影响的模块/接口] | [处理建议] |
| ⚠️ 中 | [需要关注的风险] | [影响范围] | [处理建议] |
| 💡 低 | [轻微风险或优化建议] | [影响范围] | [处理建议] |

#### 待确认事项

| 序号 | 事项 | 原因 | 负责人 |
| --- | --- | --- | --- |
| 1 | [需要确认的事项] | [为什么需要确认] | - |
| 2 | [需要确认的事项] | [为什么需要确认] | - |
```

### 总结要求

1. **整体总结**：先用一句话概括修改目的，再用列表列出所有关键变更点
2. **文件详情**：按文件路径列表，每个文件总结其具体修改内容
3. **表达清晰**：使用技术术语准确描述，如"签名"、"参数"、"结构体"等
4. **逻辑分组**：相关的修改点放在一起描述
5. **风险分析**：识别潜在风险，按严重程度分级
6. **待确认事项**：列出需要人工确认的问题点

### 风险识别要点

分析代码变更时，重点关注以下风险类型：

| 风险类型 | 触发条件 | 风险等级 |
| --- | --- | --- |
| **接口变更** | Proto/API 新增/删除/修改字段 | 中-高 |
| **依赖变更** | go.mod/package.json 版本升级或新增依赖 | 中 |
| **参数来源变更** | 函数参数、变量来源发生变化 | 高 |
| **并发安全** | 涉及共享变量、锁、goroutine | 高 |
| **错误处理** | 新增调用但未处理错误，或改变错误处理逻辑 | 中-高 |
| **性能影响** | 新增同步调用、循环内操作、大对象拷贝 | 中 |
| **配置变更** | 修改配置项、环境变量、默认值 | 中 |
| **数据库操作** | SQL 变更、索引、事务范围 | 高 |
| **安全相关** | 认证、鉴权、敏感数据处理 | 高 |
| **兼容性** | 新增字段默认值、老客户端行为 | 中 |

---

## 📚 关键资源

- **脚本工具**：`scripts/main.py` - 核心 diff 工具
- **使用指南**：`references/guide.md` - 详细使用说明
