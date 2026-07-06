import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sync_skills import find_vault_skills, check_registration, fix_registration


def make_skill(vault: Path, category: str, name: str) -> Path:
    d = vault / "skills" / category / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n## Purpose\n")
    return d


def test_find_vault_skills(tmp_path):
    make_skill(tmp_path, "1-literature", "paper-digest")
    make_skill(tmp_path, "4-writing", "auto-cite")
    skills = find_vault_skills(tmp_path)
    assert {s.name for s in skills} == {"paper-digest", "auto-cite"}


def test_check_reports_missing_and_broken(tmp_path):
    make_skill(tmp_path, "4-writing", "auto-cite")
    reg = tmp_path / ".claude" / "skills"
    reg.mkdir(parents=True)
    os.symlink("../../skills/nonexistent", reg / "ghost")
    missing, broken = check_registration(tmp_path)
    assert [s.name for s in missing] == ["auto-cite"]
    assert [p.name for p in broken] == ["ghost"]


def test_fix_creates_relative_symlinks(tmp_path):
    skill_dir = make_skill(tmp_path, "4-writing", "auto-cite")
    fix_registration(tmp_path)
    link = tmp_path / ".claude" / "skills" / "auto-cite"
    assert link.is_symlink()
    assert not os.path.isabs(os.readlink(link))
    assert link.resolve() == skill_dir.resolve()
    missing, broken = check_registration(tmp_path)
    assert missing == [] and broken == []


def test_fix_skips_non_symlink_conflict(tmp_path):
    make_skill(tmp_path, "4-writing", "auto-cite")
    reg = tmp_path / ".claude" / "skills"
    reg.mkdir(parents=True)
    conflict = reg / "auto-cite"
    conflict.mkdir()
    (conflict / "keep.txt").write_text("do not touch")
    conflicts = fix_registration(tmp_path)
    assert conflicts == [conflict]
    assert conflict.is_dir() and not conflict.is_symlink()
    assert (conflict / "keep.txt").read_text() == "do not touch"


def test_fix_repoints_wrong_symlink(tmp_path):
    skill_dir = make_skill(tmp_path, "4-writing", "auto-cite")
    other = tmp_path / "elsewhere"
    other.mkdir()
    reg = tmp_path / ".claude" / "skills"
    reg.mkdir(parents=True)
    os.symlink("../../elsewhere", reg / "auto-cite")
    conflicts = fix_registration(tmp_path)
    assert conflicts == []
    link = reg / "auto-cite"
    assert link.is_symlink()
    assert not os.path.isabs(os.readlink(link))
    assert link.resolve() == skill_dir.resolve()
