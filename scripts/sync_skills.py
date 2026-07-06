#!/usr/bin/env python3
"""校验/修复 vault skill 在 .claude/skills/ 的注册（相对 symlink）。

用法:
    python3 scripts/sync_skills.py          # 校验，发现问题 exit 1
    python3 scripts/sync_skills.py --fix    # 为缺失的 skill 创建相对 symlink
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_vault_skills(root: Path) -> list[Path]:
    """skills/<category>/<name>/SKILL.md → 返回 skill 目录列表。"""
    return sorted(p.parent for p in root.glob("skills/*/*/SKILL.md"))


def check_registration(root: Path) -> tuple[list[Path], list[Path]]:
    """返回 (未注册的 skill 目录, .claude/skills 下悬空的 symlink)。"""
    reg = root / ".claude" / "skills"
    missing = []
    for skill in find_vault_skills(root):
        link = reg / skill.name
        if not (link.is_symlink() and link.resolve() == skill.resolve()):
            missing.append(skill)
    broken = []
    if reg.is_dir():
        for link in sorted(reg.iterdir()):
            if link.is_symlink() and not link.resolve().exists():
                broken.append(link)
    return missing, broken


def fix_registration(root: Path) -> list[Path]:
    """为缺失的 skill 创建相对 symlink；返回跳过的非 symlink 冲突路径（留给人工处理）。"""
    reg = root / ".claude" / "skills"
    reg.mkdir(parents=True, exist_ok=True)
    conflicts = []
    for skill in check_registration(root)[0]:
        link = reg / skill.name
        if link.exists() and not link.is_symlink():
            conflicts.append(link)
            continue
        if link.is_symlink():
            link.unlink()
        link.symlink_to(Path(os.path.relpath(skill, reg)))
    return conflicts


def main() -> int:
    fix = "--fix" in sys.argv
    if fix:
        fix_registration(ROOT)
    missing, broken = check_registration(ROOT)
    reg = ROOT / ".claude" / "skills"
    for s in missing:
        link = reg / s.name
        if link.exists() and not link.is_symlink():
            print(f"CONFLICT: .claude/skills/{s.name} 是普通文件/目录，请人工处理")
        else:
            print(f"MISSING: {s.relative_to(ROOT)} 未注册到 .claude/skills/")
    for b in broken:
        print(f"BROKEN: {b} 指向不存在的目标")
    if missing or broken:
        print("提示: 运行 python3 scripts/sync_skills.py --fix 修复缺失注册；悬空 symlink / CONFLICT 请人工确认后处理")
        return 1
    print(f"OK: {len(find_vault_skills(ROOT))} 个 skill 全部已注册")
    return 0


if __name__ == "__main__":
    sys.exit(main())
