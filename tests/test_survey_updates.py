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


def test_match_multiline_tags(tmp_path):
    """多行 YAML list 形式的 tags 也要参与匹配。"""
    make_vault(tmp_path)
    paper = tmp_path / "Papers" / "2607-MultiTag.md"
    paper.write_text("---\ntitle: MultiTag benchmark\ntags:\n  - web-agent\n  - benchmark\n---\n")
    assert match_surveys(paper, tmp_path) == ["GUIAgent-Survey"]


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


def test_corrupt_json_backed_up_and_recovered(tmp_path):
    """损坏的账本不能被静默丢弃：备份为 .bak 后重建，record 仍可用。"""
    paper = make_vault(tmp_path)
    ledger = tmp_path / "Workbench" / "survey-updates.json"
    ledger.write_text("{not valid json", encoding="utf-8")
    assert load_pending(tmp_path) == []
    assert (tmp_path / "Workbench" / "survey-updates.json.bak").exists()
    record(paper, tmp_path)
    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert len(data["pending"]) == 1


def test_wrong_shape_json_treated_as_corrupt(tmp_path):
    """合法 JSON 但结构错误（如 [] 或缺 pending）同样视为损坏。"""
    make_vault(tmp_path)
    ledger = tmp_path / "Workbench" / "survey-updates.json"
    ledger.write_text("[]", encoding="utf-8")
    assert load_pending(tmp_path) == []
    assert (tmp_path / "Workbench" / "survey-updates.json.bak").exists()


def test_no_substring_false_positive(tmp_path):
    """词边界：keyword 'cua' 不得命中 'evacuation'。"""
    make_vault(tmp_path)
    (tmp_path / "Topics" / "ComputerUse-Survey.md").write_text(
        "---\ntitle: Computer Use Survey\nkeywords: [cua]\ndomain_map: GUI-Agent\n---\n"
    )
    paper = tmp_path / "Papers" / "2607-Crowd.md"
    paper.write_text("---\ntitle: Simulating crowd evacuation dynamics\ntags: [simulation]\n---\n")
    assert match_surveys(paper, tmp_path) == []


def test_no_cross_tag_phrase_match(tmp_path):
    """多词 keyword 不得跨 tag 边界拼接命中：[x-gui, agent-y] 不含 'gui agent'。"""
    make_vault(tmp_path)
    paper = tmp_path / "Papers" / "2607-CrossTag.md"
    paper.write_text("---\ntitle: Something unrelated\ntags: [x-gui, agent-y]\n---\n")
    assert match_surveys(paper, tmp_path) == []


def test_plural_keyword_match(tmp_path):
    """可选复数：keyword 'vlm' 须命中标题中的 'VLMs'。"""
    make_vault(tmp_path)
    paper = tmp_path / "Papers" / "2607-VlmSurvey.md"
    paper.write_text("---\ntitle: A survey of VLMs\ntags: [misc]\n---\n")
    assert match_surveys(paper, tmp_path) == ["VLM-Survey"]
