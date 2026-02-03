# git-diff

> Git 修改总结工具 - 帮助 AI 理解和总结代码变更

## 📖 目录

- [快速开始](#-快速开始)
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

## 💡 使用指南

详细使用说明请参考 [使用指南](references/guide.md)。

## 📁 目录结构

```
git-diff/
├── SKILL.md          # Skill 入口文档
├── README.md         # 详细说明
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
| 1.0.0 | 2026-02-03 | 初始版本，支持 summary/log/diff 命令 |

## 📄 许可证

MIT License

---

Created by xiaohangxu
