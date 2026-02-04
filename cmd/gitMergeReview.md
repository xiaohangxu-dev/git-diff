# Git 合并 Review

分析最近一次 merge 的详细情况，检查冲突解决和潜在风险。

## 使用场景

- 代码合并后检查冲突解决是否正确
- 审查 merge commit，确认没有代码丢失
- 分析两个分支合并时的修改冲突
- 合并后发现问题时追溯原因

## 使用方式

### 分析最近一次 merge

```
/gitMergeReview
```

### 指定 merge commit 分析

```
/gitMergeReview abc1234
```

## 执行流程

**重要：必须使用 `git-diff` skill 来完成此任务。**

1. **加载 skill**：首先调用 `use_skill` 工具加载 `git-diff` skill
2. **按照 skill 指引执行**：skill 加载后会提供详细的执行步骤和输出格式要求
3. **处理用户参数**：
   - 无参数：分析最近一次 merge commit
   - 指定 commit：分析指定的 merge commit
4. **生成标准化输出**：按照 skill 定义的格式输出结果，并追加写入到生成的 Markdown 文件末尾

## 脚本命令

```bash
# 分析最近一次 merge
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py merge-review

# 分析指定 merge commit
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py merge-review --commit <merge_commit>

# 指定输出文件
cd <项目根目录> && python3 <SKILL_DIR>/scripts/main.py merge-review -o merge_review.md
```

## 输出内容

- **合并信息**：merge commit 基本信息，包含两个 parent 分支
- **冲突分析**：识别两边都修改的文件及其解决方式
- **风险提示**：可能丢失的修改、需要人工检查的文件
- **分支修改统计**：两个 parent 分支各自的修改情况
- **合并结果统计**：最终合并后的文件变更统计

## 冲突解决类型说明

| 解决类型 | 说明 | 风险等级 |
| --- | --- | --- |
| 保留主分支 | 完全使用 parent1 的内容 | ⚠️ 中 - 被合并分支的修改可能丢失 |
| 保留被合并分支 | 完全使用 parent2 的内容 | ⚠️ 中 - 主分支的修改可能丢失 |
| 相同修改 | 两边修改内容一致 | ✅ 低 - 无风险 |
| 手动合并 | 两边修改都有保留 | 🔍 需检查 - 建议人工验证 |

## 示例

### 分析最近一次 merge

输入：
```
/gitMergeReview
```

输出：
```markdown
## 合并信息

| 项目 | 值 |
| --- | --- |
| Merge Commit | `abc1234` |
| 提交信息 | Merge branch 'feature/login' into main |
| Parent 1 (主分支) | `def5678` (origin/main) |
| Parent 2 (被合并) | `ghi9012` (feature/login) |

## 冲突分析

⚠️ 发现 **3** 个潜在冲突文件（两边都有修改）

| 文件 | 解决方式 | 风险等级 |
| --- | --- | --- |
| `service/user.go` | 手动合并 | 🔍 需检查 |
| `config/app.yaml` | 保留主分支 | ⚠️ 中 |
| `utils/common.go` | 相同修改 | ✅ 低 |

## 风险提示

### ⚠️ 可能丢失的修改

- `config/app.yaml`: parent2 的修改可能被丢弃

### 🔍 需要人工检查的文件

- `service/user.go`

#### AI 分析总结

本次合并将 feature/login 分支合并到 main 分支...

- 用户登录功能代码已正确合并
- config/app.yaml 中的新配置项被覆盖，需要确认是否需要保留
- ...
```

## 注意事项

1. 该命令只能分析 merge commit（有两个 parent 的 commit）
2. 如果当前分支没有 merge commit，需要使用 `--commit` 指定
3. 使用 `git log --merges` 可以查看所有 merge 历史
4. 分析结果会自动保存到 `.codebuddy/git-diff/` 目录
