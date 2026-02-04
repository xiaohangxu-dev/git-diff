#!/usr/bin/env python3
"""
git-diff 主脚本 - Git 修改总结工具

功能:
    1. 总结修改: 对比源分支和当前分支的修改
    2. 指定范围总结: 列出 git log，选择 commit 范围进行 diff 总结
    3. 合并 Review: 查看最近一次合并的详细信息，分析冲突解决和潜在风险

Usage:
    python3 main.py --help
    python3 main.py summary [--source <branch>] [-o <file>]
    python3 main.py log [--limit <n>]
    python3 main.py diff --from <commit> [--to <commit>] [-o <file>]
    python3 main.py merge-review [--commit <merge_commit>] [-o <file>]
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, TextIO


# 默认输出文件路径
DEFAULT_OUTPUT_DIR = ".codebuddy/git-diff"


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """将文本转换为安全的文件名
    
    Args:
        text: 原始文本（如 commit message）
        max_length: 最大长度
        
    Returns:
        安全的文件名字符串
    """
    if not text:
        return "changes"
    
    # 移除或替换不安全的字符
    # 保留中文、英文、数字、下划线、短横线
    safe_text = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', text)
    # 合并多个下划线
    safe_text = re.sub(r'_+', '_', safe_text)
    # 移除首尾下划线
    safe_text = safe_text.strip('_')
    # 截断长度
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length].rstrip('_')
    
    return safe_text if safe_text else "changes"


def get_commit_summary(from_ref: str, to_ref: str = "HEAD") -> str:
    """从 commit 信息中提取摘要作为文件名
    
    优先使用最新的 commit message，如果有多个 commit 则尝试提取共同特征
    """
    # 获取最新一条 commit 的 message
    code, stdout, _ = run_git_command([
        "log", "-1", "--format=%s", to_ref
    ])
    
    if code == 0 and stdout.strip():
        message = stdout.strip()
        # 提取 commit message 的关键部分
        # 常见格式: "feat: xxx", "fix(scope): xxx", "类型: 描述"
        
        # 尝试匹配常见的 commit 格式
        patterns = [
            r'^(?:feat|fix|docs|style|refactor|test|chore|perf)(?:\([^)]+\))?:\s*(.+)',  # conventional commits
            r'^(?:新增|修复|优化|重构|文档|测试|配置)[：:]\s*(.+)',  # 中文格式
            r'^(.+)',  # 直接使用整个 message
        ]
        
        for pattern in patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                return sanitize_filename(match.group(1) if match.lastindex else message)
    
    return "changes"


class OutputWriter:
    """输出写入器，支持同时输出到控制台和文件"""
    
    def __init__(self, file_path: Optional[str] = None):
        self.file: Optional[TextIO] = None
        self.file_path = file_path
        if file_path:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            self.file = open(file_path, 'w', encoding='utf-8')
    
    def write(self, text: str = "", end: str = "\n"):
        """写入内容（同时输出到控制台和文件）"""
        output = text + end
        # 始终输出到控制台
        print(text, end=end)
        # 如果有文件，也写入文件
        if self.file:
            self.file.write(output)
    
    def write_console_only(self, text: str = "", end: str = "\n"):
        """只输出到控制台，不写入文件"""
        print(text, end=end)
    
    def close(self):
        """关闭文件"""
        if self.file:
            self.file.close()
            print(f"\n✅ 结果已保存到: {self.file_path}")


def run_git_command(args: list[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """执行 git 命令并返回结果"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", "git 命令未找到，请确保已安装 git"


def get_current_branch() -> Optional[str]:
    """获取当前分支名"""
    code, stdout, _ = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    if code == 0:
        return stdout.strip()
    return None


def get_source_branch() -> Optional[str]:
    """尝试获取源分支（当前分支是从哪个分支 checkout 出来的）
    
    检测顺序（优先主干分支，因为大多数分支都是从主干创建的）:
    1. origin/master 或 origin/main（远程主干）
    2. master 或 main（本地主干）
    3. 上游分支（如果设置了的话）
    """
    current = get_current_branch()
    
    # 优先检测远程主干分支
    for branch in ["origin/master", "origin/main"]:
        code, _, _ = run_git_command(["rev-parse", "--verify", branch])
        if code == 0:
            # 验证能找到 merge-base（确保有共同历史）
            mb_code, mb_out, _ = run_git_command(["merge-base", branch, "HEAD"])
            if mb_code == 0 and mb_out.strip():
                return branch
    
    # 检测本地主干分支
    for branch in ["master", "main"]:
        if branch == current:  # 跳过当前分支
            continue
        code, _, _ = run_git_command(["rev-parse", "--verify", branch])
        if code == 0:
            mb_code, mb_out, _ = run_git_command(["merge-base", branch, "HEAD"])
            if mb_code == 0 and mb_out.strip():
                return branch
    
    # 最后尝试上游分支
    code, stdout, _ = run_git_command(["rev-parse", "--abbrev-ref", "@{upstream}"])
    if code == 0:
        upstream = stdout.strip()
        verify_code, _, _ = run_git_command(["rev-parse", "--verify", upstream])
        if verify_code == 0:
            return upstream
    
    return None


def get_merge_base(branch1: str, branch2: str) -> Optional[str]:
    """获取两个分支的分叉点（fork point）
    
    这是当前分支从源分支 checkout 出来的那个 commit
    """
    # 优先使用 --fork-point，更准确地找到分叉点
    code, stdout, _ = run_git_command(["merge-base", "--fork-point", branch1, branch2])
    if code == 0 and stdout.strip():
        return stdout.strip()
    
    # 回退到普通 merge-base
    code, stdout, _ = run_git_command(["merge-base", branch1, branch2])
    if code == 0:
        return stdout.strip()
    return None


def get_default_output_path(from_ref: str = "", to_ref: str = "HEAD") -> str:
    """获取默认输出文件路径
    
    文件名格式: <commit摘要>_<时间戳>.md
    例如: feat_添加用户登录功能_20260203_143025.md
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = get_commit_summary(from_ref, to_ref)
    filename = f"{summary}_{timestamp}.md"
    return str(Path(DEFAULT_OUTPUT_DIR) / filename)


def cmd_summary(args) -> int:
    """功能1: 总结源分支和当前分支之间的修改"""
    current_branch = get_current_branch()
    if not current_branch:
        print("错误: 无法获取当前分支", file=sys.stderr)
        return 1
    
    source_branch = args.source or get_source_branch()
    if not source_branch:
        print("错误: 无法确定源分支", file=sys.stderr)
        print("请使用 --source 指定，例如:", file=sys.stderr)
        print("  --source origin/main", file=sys.stderr)
        print("  --source origin/master", file=sys.stderr)
        print("  --source main", file=sys.stderr)
        return 1
    
    # 获取 merge base
    merge_base = get_merge_base(source_branch, current_branch)
    if not merge_base:
        print(f"错误: 无法找到 '{source_branch}' 和 '{current_branch}' 的共同祖先", file=sys.stderr)
        print("", file=sys.stderr)
        print("可能的原因:", file=sys.stderr)
        print("  1. 两个分支没有共同历史", file=sys.stderr)
        print("  2. 源分支名称不正确", file=sys.stderr)
        print("", file=sys.stderr)
        print("请尝试:", file=sys.stderr)
        print("  1. 使用 --source 指定正确的源分支", file=sys.stderr)
        print("  2. 使用 'git branch -a' 查看所有分支", file=sys.stderr)
        print("  3. 使用 'diff --from <commit>' 指定具体的 commit 范围", file=sys.stderr)
        return 1
    
    # 确定输出路径
    output_path = args.output if args.output else get_default_output_path(merge_base, "HEAD")
    out = OutputWriter(output_path)
    
    try:
        out.write(f"# Git 修改总结")
        out.write()
        out.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        out.write()
        out.write(f"## 基本信息")
        out.write()
        out.write(f"| 项目 | 值 |")
        out.write(f"| --- | --- |")
        out.write(f"| 源分支 | `{source_branch}` |")
        out.write(f"| 当前分支 | `{current_branch}` |")
        out.write(f"| 共同祖先 | `{merge_base[:8]}` |")
        out.write()
        
        # 获取 commit 列表
        out.write(f"## Commit 列表")
        out.write()
        code, stdout, stderr = run_git_command([
            "log", "--oneline", "--no-decorate",
            f"{merge_base}..HEAD"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        commits = stdout.strip()
        if commits:
            out.write("```")
            out.write(commits)
            out.write("```")
        else:
            out.write("_(无新 commit)_")
        out.write()
        
        # 获取文件变更统计
        out.write(f"## 文件变更统计")
        out.write()
        code, stdout, stderr = run_git_command([
            "diff", "--stat", f"{merge_base}..HEAD"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        if stdout.strip():
            out.write("```")
            out.write(stdout.rstrip())
            out.write("```")
        else:
            out.write("_(无文件变更)_")
        
        # 获取详细 diff（只输出到控制台，供大模型分析，不写入文件）
        out.write_console_only()
        out.write_console_only(f"## 详细变更内容")
        out.write_console_only()
        code, stdout, stderr = run_git_command([
            "diff", f"{merge_base}..HEAD"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        if stdout.strip():
            out.write_console_only("```diff")
            out.write_console_only(stdout.rstrip())
            out.write_console_only("```")
        else:
            out.write_console_only("_(无变更内容)_")
        
    finally:
        out.close()
    
    return 0


def cmd_log(args) -> int:
    """功能2辅助: 列出 git log 供用户选择 commit"""
    limit = args.limit or 20
    
    print(f"📜 最近 {limit} 条 Commit 记录:")
    print("=" * 70)
    print(f"{'序号':<4} {'Commit ID':<10} {'日期':<12} {'提交信息'}")
    print("-" * 70)
    
    code, stdout, stderr = run_git_command([
        "log", f"-{limit}",
        "--format=%h|%ad|%s",
        "--date=short"
    ])
    
    if code != 0:
        print(f"错误: {stderr}", file=sys.stderr)
        return 1
    
    lines = stdout.strip().split("\n")
    for i, line in enumerate(lines, 1):
        if line:
            parts = line.split("|", 2)
            if len(parts) >= 3:
                commit_id, date, message = parts
                if len(message) > 40:
                    message = message[:37] + "..."
                print(f"{i:<4} {commit_id:<10} {date:<12} {message}")
    
    print("-" * 70)
    print()
    print("💡 使用提示:")
    print("   使用 'diff --from <commit_id>' 指定起始 commit")
    print("   使用 'diff --from <commit_id> --to <commit_id>' 指定范围")
    print("   默认 --to 为 HEAD")
    
    return 0


def find_latest_merge_commit() -> Optional[str]:
    """查找最近一次 merge commit"""
    # 使用 --merges 只筛选 merge commits
    code, stdout, _ = run_git_command([
        "log", "--merges", "-1", "--format=%H"
    ])
    if code == 0 and stdout.strip():
        return stdout.strip()
    return None


def get_merge_parents(merge_commit: str) -> Optional[Tuple[str, str]]:
    """获取 merge commit 的两个父 commit
    
    Returns:
        (parent1, parent2) - parent1 通常是主分支，parent2 是被合并的分支
    """
    code, stdout, _ = run_git_command([
        "rev-parse", f"{merge_commit}^1", f"{merge_commit}^2"
    ])
    if code == 0:
        parents = stdout.strip().split('\n')
        if len(parents) >= 2:
            return (parents[0].strip(), parents[1].strip())
    return None


def get_commit_info(commit: str) -> dict:
    """获取 commit 的详细信息"""
    code, stdout, _ = run_git_command([
        "log", "-1", "--format=%H|%h|%s|%an|%ad|%P",
        "--date=short", commit
    ])
    if code == 0 and stdout.strip():
        parts = stdout.strip().split('|')
        if len(parts) >= 6:
            return {
                'hash': parts[0],
                'short_hash': parts[1],
                'subject': parts[2],
                'author': parts[3],
                'date': parts[4],
                'parents': parts[5].split() if parts[5] else []
            }
    return {}


def get_branch_name_for_commit(commit: str) -> str:
    """尝试获取 commit 所属的分支名"""
    # 尝试通过 reflog 或 branch --contains 获取
    code, stdout, _ = run_git_command([
        "branch", "-a", "--contains", commit
    ])
    if code == 0 and stdout.strip():
        branches = [b.strip().lstrip('* ') for b in stdout.strip().split('\n')]
        # 过滤掉 HEAD detached 等
        branches = [b for b in branches if b and 'HEAD' not in b]
        if branches:
            return branches[0]
    return commit[:8]


def analyze_merge_conflicts(merge_commit: str, parent1: str, parent2: str) -> dict:
    """分析合并中的冲突解决情况
    
    通过比较三方 diff 来识别可能的冲突文件和解决方式
    """
    result = {
        'conflict_files': [],
        'lost_changes': [],
        'manual_resolutions': []
    }
    
    # 获取 merge base（两个 parent 的共同祖先）
    merge_base = get_merge_base(parent1, parent2)
    if not merge_base:
        return result
    
    # 获取 parent1 相对于 merge-base 修改的文件
    code1, files1, _ = run_git_command([
        "diff", "--name-only", f"{merge_base}..{parent1}"
    ])
    parent1_files = set(files1.strip().split('\n')) if code1 == 0 and files1.strip() else set()
    
    # 获取 parent2 相对于 merge-base 修改的文件
    code2, files2, _ = run_git_command([
        "diff", "--name-only", f"{merge_base}..{parent2}"
    ])
    parent2_files = set(files2.strip().split('\n')) if code2 == 0 and files2.strip() else set()
    
    # 两边都修改的文件（潜在冲突）
    potential_conflicts = parent1_files & parent2_files
    
    for file in potential_conflicts:
        if not file:
            continue
            
        # 对每个潜在冲突文件，比较最终结果
        conflict_info = {
            'file': file,
            'parent1_changes': '',
            'parent2_changes': '',
            'merge_result': '',
            'resolution_type': 'unknown'
        }
        
        # 获取 parent1 的修改
        code, p1_diff, _ = run_git_command([
            "diff", f"{merge_base}..{parent1}", "--", file
        ])
        if code == 0:
            conflict_info['parent1_diff'] = p1_diff
        
        # 获取 parent2 的修改
        code, p2_diff, _ = run_git_command([
            "diff", f"{merge_base}..{parent2}", "--", file
        ])
        if code == 0:
            conflict_info['parent2_diff'] = p2_diff
        
        # 获取最终 merge 结果相对于 merge-base 的变化
        code, merge_diff, _ = run_git_command([
            "diff", f"{merge_base}..{merge_commit}", "--", file
        ])
        if code == 0:
            conflict_info['merge_diff'] = merge_diff
        
        # 分析解决方式
        # 比较 merge 结果与各个 parent 的差异
        code, diff_vs_p1, _ = run_git_command([
            "diff", f"{parent1}..{merge_commit}", "--", file
        ])
        code, diff_vs_p2, _ = run_git_command([
            "diff", f"{parent2}..{merge_commit}", "--", file
        ])
        
        # 判断解决类型
        if not diff_vs_p1.strip() and diff_vs_p2.strip():
            conflict_info['resolution_type'] = 'kept_parent1'
            conflict_info['risk'] = 'parent2 的修改可能被丢弃'
            result['lost_changes'].append({
                'file': file,
                'lost_from': 'parent2',
                'diff': p2_diff if 'p2_diff' in dir() else ''
            })
        elif not diff_vs_p2.strip() and diff_vs_p1.strip():
            conflict_info['resolution_type'] = 'kept_parent2'
            conflict_info['risk'] = 'parent1 的修改可能被丢弃'
            result['lost_changes'].append({
                'file': file,
                'lost_from': 'parent1',
                'diff': p1_diff if 'p1_diff' in dir() else ''
            })
        elif not diff_vs_p1.strip() and not diff_vs_p2.strip():
            conflict_info['resolution_type'] = 'identical'
        else:
            conflict_info['resolution_type'] = 'manual_merge'
            result['manual_resolutions'].append(conflict_info)
        
        result['conflict_files'].append(conflict_info)
    
    return result


def cmd_merge_review(args) -> int:
    """功能3: 合并 Review - 分析最近一次 merge 的详细情况"""
    
    # 确定要分析的 merge commit
    merge_commit = args.commit
    if not merge_commit:
        merge_commit = find_latest_merge_commit()
        if not merge_commit:
            print("错误: 当前分支没有找到 merge commit", file=sys.stderr)
            print("", file=sys.stderr)
            print("提示:", file=sys.stderr)
            print("  1. 使用 --commit 指定 merge commit", file=sys.stderr)
            print("  2. 使用 'git log --merges' 查看 merge 历史", file=sys.stderr)
            return 1
    
    # 验证是否为 merge commit
    commit_info = get_commit_info(merge_commit)
    if not commit_info:
        print(f"错误: 无法获取 commit '{merge_commit}' 的信息", file=sys.stderr)
        return 1
    
    if len(commit_info.get('parents', [])) < 2:
        print(f"错误: '{merge_commit}' 不是一个 merge commit", file=sys.stderr)
        print("提示: merge commit 应该有两个 parent", file=sys.stderr)
        return 1
    
    parents = get_merge_parents(merge_commit)
    if not parents:
        print(f"错误: 无法获取 merge commit 的 parent 信息", file=sys.stderr)
        return 1
    
    parent1, parent2 = parents
    
    # 获取 parent 信息
    parent1_info = get_commit_info(parent1)
    parent2_info = get_commit_info(parent2)
    
    # 尝试获取分支名
    parent1_branch = get_branch_name_for_commit(parent1)
    parent2_branch = get_branch_name_for_commit(parent2)
    
    # 获取 merge base
    merge_base = get_merge_base(parent1, parent2)
    
    # 确定输出路径
    output_path = args.output if args.output else get_default_output_path(merge_base or parent1, merge_commit)
    out = OutputWriter(output_path)
    
    try:
        out.write("# Merge Review 报告")
        out.write()
        out.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        out.write()
        
        # 基本信息
        out.write("## 合并信息")
        out.write()
        out.write("| 项目 | 值 |")
        out.write("| --- | --- |")
        out.write(f"| Merge Commit | `{commit_info['short_hash']}` |")
        out.write(f"| 提交信息 | {commit_info['subject']} |")
        out.write(f"| 作者 | {commit_info['author']} |")
        out.write(f"| 日期 | {commit_info['date']} |")
        out.write(f"| Parent 1 (主分支) | `{parent1[:8]}` ({parent1_branch}) |")
        out.write(f"| Parent 2 (被合并) | `{parent2[:8]}` ({parent2_branch}) |")
        if merge_base:
            out.write(f"| Merge Base | `{merge_base[:8]}` |")
        out.write()
        
        # 分析冲突解决
        out.write("## 冲突分析")
        out.write()
        
        conflict_analysis = analyze_merge_conflicts(merge_commit, parent1, parent2)
        
        if not conflict_analysis['conflict_files']:
            out.write("✅ 无冲突文件（两个分支修改了不同的文件）")
        else:
            out.write(f"⚠️ 发现 **{len(conflict_analysis['conflict_files'])}** 个潜在冲突文件（两边都有修改）")
            out.write()
            out.write("| 文件 | 解决方式 | 风险等级 |")
            out.write("| --- | --- | --- |")
            
            for cf in conflict_analysis['conflict_files']:
                resolution = cf['resolution_type']
                if resolution == 'kept_parent1':
                    resolution_text = "保留主分支"
                    risk = "⚠️ 中"
                elif resolution == 'kept_parent2':
                    resolution_text = "保留被合并分支"
                    risk = "⚠️ 中"
                elif resolution == 'identical':
                    resolution_text = "相同修改"
                    risk = "✅ 低"
                else:
                    resolution_text = "手动合并"
                    risk = "🔍 需检查"
                
                out.write(f"| `{cf['file']}` | {resolution_text} | {risk} |")
        out.write()
        
        # 风险提示
        out.write("## 风险提示")
        out.write()
        
        if conflict_analysis['lost_changes']:
            out.write("### ⚠️ 可能丢失的修改")
            out.write()
            out.write("以下文件在合并时，一方的修改可能被完全覆盖：")
            out.write()
            for lost in conflict_analysis['lost_changes']:
                out.write(f"- `{lost['file']}`: {lost['lost_from']} 的修改可能被丢弃")
            out.write()
        else:
            out.write("✅ 未发现明显的代码丢失风险")
            out.write()
        
        if conflict_analysis['manual_resolutions']:
            out.write("### 🔍 需要人工检查的文件")
            out.write()
            out.write("以下文件经过手动合并，建议检查合并结果是否正确：")
            out.write()
            for mr in conflict_analysis['manual_resolutions']:
                out.write(f"- `{mr['file']}`")
            out.write()
        
        # Parent1 的修改（主分支）
        out.write(f"## Parent 1 修改（{parent1_branch}）")
        out.write()
        if merge_base:
            code, stdout, _ = run_git_command([
                "diff", "--stat", f"{merge_base}..{parent1}"
            ])
            if code == 0 and stdout.strip():
                out.write("```")
                out.write(stdout.rstrip())
                out.write("```")
            else:
                out.write("_(无修改)_")
        out.write()
        
        # Parent2 的修改（被合并分支）
        out.write(f"## Parent 2 修改（{parent2_branch}）")
        out.write()
        if merge_base:
            code, stdout, _ = run_git_command([
                "diff", "--stat", f"{merge_base}..{parent2}"
            ])
            if code == 0 and stdout.strip():
                out.write("```")
                out.write(stdout.rstrip())
                out.write("```")
            else:
                out.write("_(无修改)_")
        out.write()
        
        # 最终合并结果
        out.write("## 合并结果统计")
        out.write()
        if merge_base:
            code, stdout, _ = run_git_command([
                "diff", "--stat", f"{merge_base}..{merge_commit}"
            ])
            if code == 0 and stdout.strip():
                out.write("```")
                out.write(stdout.rstrip())
                out.write("```")
            else:
                out.write("_(无变更)_")
        
        # 详细 diff 输出到控制台供 AI 分析
        out.write_console_only()
        out.write_console_only("## 详细变更内容")
        out.write_console_only()
        
        # 输出潜在冲突文件的三方对比
        if conflict_analysis['conflict_files']:
            out.write_console_only("### 冲突文件详细对比")
            out.write_console_only()
            
            for cf in conflict_analysis['conflict_files']:
                out.write_console_only(f"#### 文件: `{cf['file']}` (解决方式: {cf['resolution_type']})")
                out.write_console_only()
                
                if cf.get('parent1_diff'):
                    out.write_console_only(f"**Parent 1 ({parent1_branch}) 的修改:**")
                    out.write_console_only("```diff")
                    out.write_console_only(cf['parent1_diff'].rstrip())
                    out.write_console_only("```")
                    out.write_console_only()
                
                if cf.get('parent2_diff'):
                    out.write_console_only(f"**Parent 2 ({parent2_branch}) 的修改:**")
                    out.write_console_only("```diff")
                    out.write_console_only(cf['parent2_diff'].rstrip())
                    out.write_console_only("```")
                    out.write_console_only()
                
                if cf.get('merge_diff'):
                    out.write_console_only("**最终合并结果:**")
                    out.write_console_only("```diff")
                    out.write_console_only(cf['merge_diff'].rstrip())
                    out.write_console_only("```")
                    out.write_console_only()
        
    finally:
        out.close()
    
    return 0


def cmd_diff(args) -> int:
    """功能2: 指定 commit 范围进行 diff"""
    from_commit = args.from_commit
    to_commit = args.to_commit or "HEAD"
    
    # 验证 commit 是否存在
    code, _, stderr = run_git_command(["rev-parse", "--verify", from_commit])
    if code != 0:
        print(f"错误: 无效的起始 commit '{from_commit}'", file=sys.stderr)
        return 1
    
    code, _, stderr = run_git_command(["rev-parse", "--verify", to_commit])
    if code != 0:
        print(f"错误: 无效的结束 commit '{to_commit}'", file=sys.stderr)
        return 1
    
    # 确定输出路径
    output_path = args.output if args.output else get_default_output_path(from_commit, to_commit)
    out = OutputWriter(output_path)
    
    try:
        out.write(f"# Git Diff 范围总结")
        out.write()
        out.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        out.write()
        out.write(f"## 基本信息")
        out.write()
        out.write(f"| 项目 | 值 |")
        out.write(f"| --- | --- |")
        out.write(f"| 起始 Commit | `{from_commit}` |")
        out.write(f"| 结束 Commit | `{to_commit}` |")
        out.write()
        
        # 获取 commit 列表
        out.write(f"## Commit 列表")
        out.write()
        code, stdout, stderr = run_git_command([
            "log", "--oneline", "--no-decorate",
            f"{from_commit}..{to_commit}"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        commits = stdout.strip()
        if commits:
            out.write("```")
            out.write(commits)
            out.write("```")
        else:
            out.write("_(无 commit)_")
        out.write()
        
        # 获取文件变更统计
        out.write(f"## 文件变更统计")
        out.write()
        code, stdout, stderr = run_git_command([
            "diff", "--stat", f"{from_commit}..{to_commit}"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        if stdout.strip():
            out.write("```")
            out.write(stdout.rstrip())
            out.write("```")
        else:
            out.write("_(无文件变更)_")
        
        # 获取详细 diff（只输出到控制台，供大模型分析，不写入文件）
        out.write_console_only()
        out.write_console_only(f"## 详细变更内容")
        out.write_console_only()
        code, stdout, stderr = run_git_command([
            "diff", f"{from_commit}..{to_commit}"
        ])
        if code != 0:
            print(f"错误: {stderr}", file=sys.stderr)
            return 1
        
        if stdout.strip():
            out.write_console_only("```diff")
            out.write_console_only(stdout.rstrip())
            out.write_console_only("```")
        else:
            out.write_console_only("_(无变更内容)_")
        
    finally:
        out.close()
    
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Git 修改总结工具 - 帮助 AI 理解代码变更",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s summary                         # 总结并输出到默认文件
  %(prog)s summary -o changes.md           # 输出到指定文件
  %(prog)s summary --source main           # 指定源分支
  %(prog)s log                             # 列出最近 20 条 commit
  %(prog)s log --limit 50                  # 列出最近 50 条 commit
  %(prog)s diff --from abc123              # 从指定 commit 到 HEAD
  %(prog)s diff --from abc123 -o diff.md   # 输出到指定文件
  %(prog)s merge-review                    # 分析最近一次 merge
  %(prog)s merge-review --commit abc123    # 分析指定 merge commit
"""
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # summary 子命令
    summary_parser = subparsers.add_parser(
        "summary",
        help="总结源分支和当前分支之间的修改"
    )
    summary_parser.add_argument(
        "--source", "-s",
        help="源分支名称（默认自动检测）"
    )
    summary_parser.add_argument(
        "--output", "-o",
        help=f"输出文件路径（默认: {DEFAULT_OUTPUT_DIR}/changes_<timestamp>.md）"
    )
    
    # log 子命令
    log_parser = subparsers.add_parser(
        "log",
        help="列出 git log 供选择 commit"
    )
    log_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=20,
        help="显示的 commit 数量（默认 20）"
    )
    
    # diff 子命令
    diff_parser = subparsers.add_parser(
        "diff",
        help="指定 commit 范围进行 diff"
    )
    diff_parser.add_argument(
        "--from", "-f",
        dest="from_commit",
        required=True,
        help="起始 commit（必填）"
    )
    diff_parser.add_argument(
        "--to", "-t",
        dest="to_commit",
        default="HEAD",
        help="结束 commit（默认 HEAD）"
    )
    diff_parser.add_argument(
        "--output", "-o",
        help=f"输出文件路径（默认: {DEFAULT_OUTPUT_DIR}/changes_<timestamp>.md）"
    )
    
    # merge-review 子命令
    merge_parser = subparsers.add_parser(
        "merge-review",
        help="分析最近一次 merge 的详细情况，检查冲突解决和潜在风险"
    )
    merge_parser.add_argument(
        "--commit", "-c",
        help="指定要分析的 merge commit（默认: 最近一次 merge）"
    )
    merge_parser.add_argument(
        "--output", "-o",
        help=f"输出文件路径（默认: {DEFAULT_OUTPUT_DIR}/merge_review_<timestamp>.md）"
    )
    
    args = parser.parse_args()
    
    if args.command == "summary":
        return cmd_summary(args)
    elif args.command == "log":
        return cmd_log(args)
    elif args.command == "diff":
        return cmd_diff(args)
    elif args.command == "merge-review":
        return cmd_merge_review(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
