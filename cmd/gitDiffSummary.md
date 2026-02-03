# Git 分支修改总结

总结当前分支相对于源分支的所有代码修改。

## 使用场景

- 想了解当前开发分支做了哪些修改
- 提交代码前回顾所有变更
- 代码审查前生成修改摘要
- 合并分支前确认修改范围

## 使用方式

直接输入以下命令之一：

```
/gitDiffSummary
```

或带参数指定源分支：

```
/gitDiffSummary main
/gitDiffSummary master
/gitDiffSummary develop
```

## 执行流程

**重要：必须使用 `git-diff` skill 来完成此任务。**

1. **加载 skill**：首先调用 `use_skill` 工具加载 `git-diff` skill
2. **按照 skill 指引执行**：skill 加载后会提供详细的执行步骤和输出格式要求
3. **生成标准化输出**：按照 skill 定义的格式输出结果

## 输出内容

- **修改总结**：一句话概括本次修改的核心目的
- **变更点列表**：列出所有关键变更点
- **文件变更详情**：按文件路径列出每个文件的具体修改内容

## 示例

输入：
```
/gitDiffSummary
```

输出：
```
#### 修改总结

增加问题分类 ID 支持，涉及请求参数、调用签名及结构体扩展等调整。

- 调整 CreateQA 请求中 AppId/PartnerId 参数来源
- 新增提前获取问题分类 ID 逻辑
- 修改 callQuestionStream 签名，增加 questionClassId 参数
- ...

#### 文件变更详情

| 文件路径 | 文件总结 |
| --- | --- |
| service/qarobot_go.go | 将 CreateQA 请求参数改为使用 req.AppId |
| logic/xxx/OnceQuestionStream.go | 导入 time 包；新增获取问题分类ID逻辑 |
```
