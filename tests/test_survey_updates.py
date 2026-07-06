import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from survey_updates import match_surveys, record, load_pending, clear


def make_vault(tmp_path):
    (tmp_path / "Topics").mkdir()
    (tmp_path / "Papers").mkdir()
    (tmp_path / "Workbench").mkdir()
    (tmp_path / "Topics" / "GUIAgent-Survey.md").write_text(
        "---\ntitle: GUI Agent Survey\nkeywords: [gui-agent, web agent]\ndomain_map: GUI-Agent\n---\n"
    )
    (tmp_path / "Topics" / "VLM-Survey.md").write_text(
        "---\ntitle: VLM Survey\nkeywords: [vlm]\ndomain_map: VLM\n---\n"
    )
    paper = tmp_path / "Papers" / "2607-FooAgent.md"
    paper.write_text("---\ntitle: FooAgent web agent benchmark\ntags: [gui-agent, benchmark]\n---\n")
    return paper


def test_match_by_tag_and_title(tmp_path):
    paper = make_vault(tmp_path)
    assert match_surveys(paper, tmp_path) == ["GUIAgent-Survey"]


def test_match_normalizes_hyphens_vs_spaces(tmp_path):
    """keyword 'web agent'（空格）必须命中 tag 'web-agent'（连字符），反向亦然。"""
    make_vault(tmp_path)
    paper = tmp_path / "Papers" / "2607-BarAgent.md"
    paper.write_text("---\ntitle: BarAgent benchmark\ntags: [web-agent]\n---\n")
    assert match_surveys(paper, tmp_path) == ["GUIAgent-Survey"]
    paper2 = tmp_path / "Papers" / "2607-BazAgent.md"
    paper2.write_text("---\ntitle: A GUI agent for spreadsheets\ntags: [misc]\n---\n")
    assert match_surveys(paper2, tmp_path) == ["GUIAgent-Survey"]


def test_record_appends_and_dedups(tmp_path):
    paper = make_vault(tmp_path)
    record(paper, tmp_path)
    record(paper, tmp_path)  # 幂等
    pending = load_pending(tmp_path)
    assert len(pending) == 1
    assert pending[0]["survey"] == "GUIAgent-Survey"
    assert pending[0]["paper"] == "Papers/2607-FooAgent.md"


def test_clear_removes_processed(tmp_path):
    paper = make_vault(tmp_path)
    record(paper, tmp_path)
    clear("GUIAgent-Survey", ["Papers/2607-FooAgent.md"], tmp_path)
    assert load_pending(tmp_path) == []


def test_missing_json_initialized(tmp_path):
    make_vault(tmp_path)
    assert load_pending(tmp_path) == []
