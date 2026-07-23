import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_paper_contract_has_claim_level_provenance():
    template = text("Templates/Paper.md")
    digest = text("skills/1-literature/paper-digest/SKILL.md")

    assert "verification_status:" in template
    assert "## Evidence Ledger" in template
    assert "Source locator" in template
    assert "--prepare-only" in digest
    assert "Finder ≠ Verifier" in digest
    assert "source-verified" in digest
    assert "prepare-only 零共享写入" in digest


def test_orchestrators_separate_roles_and_serialize_commits():
    daily = text("skills/1-literature/daily-papers/SKILL.md")
    team = text("skills/6-orchestration/research-team/SKILL.md")
    survey = text("skills/1-literature/literature-survey/SKILL.md")

    assert "独立 Reviewer" in daily
    assert "Coordinator 串行 Commit" in daily
    assert "partial summary" in daily
    assert "单写者" in team
    assert "Deep Gap Reviewer" in team
    assert "Verification Gate + Post-verification Gap Pass" in survey
    assert "最多执行 3 个定向 query" in survey


def test_memory_uses_canonical_sources_and_json_review_queue():
    memory = text("skills/5-evolution/memory-distill/SKILL.md")
    protocol = text("references/memory-protocol.md")

    assert "canonical `source_id`" in memory
    assert "日志不是证据" in memory
    assert "enqueue-review" in memory
    assert "Workbench/queue.md" not in memory
    assert "The same paper summarized on three dates remains one source" in protocol
    assert "review_insight" in protocol


def test_team_config_exposes_budget_and_role_policy():
    config = json.loads(text("Workbench/config/team-config.json"))

    assert config["digest"]["parallel_limit"] <= 4
    assert config["digest"]["prepare_parallel_limit"] < config["digest"]["parallel_limit"]
    assert config["orchestration"]["checkpoint_every"] > 0
    assert config["orchestration"]["post_verification_loops"] == 1
    assert config["model_policy"]["verifier"]["require_different_agent"] is True
    assert config["model_policy"]["verifier"]["hide_finder_reasoning"] is True


def test_run_protocol_is_resumable_and_not_evidence():
    protocol = text("references/research-run-protocol.md")

    assert '"status": "in_progress"' in protocol
    assert '"checkpoint_at"' in protocol
    assert "Coordinator is the sole manifest writer" in protocol
    assert "never count as independent evidence" in protocol


def test_no_active_protocol_points_to_legacy_markdown_queue():
    paths = [
        "README.md",
        "docs/SPEC.md",
        "skills/1-literature/paper-digest/SKILL.md",
        "skills/5-evolution/memory-distill/SKILL.md",
        "skills/5-evolution/agenda-evolve/SKILL.md",
        "skills/7-presentation/domain-presentation/SKILL.md",
    ]

    for path in paths:
        assert "Workbench/queue.md" not in text(path), path


def test_revised_markdown_contracts_have_balanced_fences():
    paths = [
        "Templates/Paper.md",
        "Templates/Survey.md",
        "references/research-run-protocol.md",
        "skills/1-literature/paper-digest/SKILL.md",
        "skills/1-literature/daily-papers/SKILL.md",
        "skills/1-literature/literature-survey/SKILL.md",
        "skills/1-literature/survey-refresh/SKILL.md",
        "skills/5-evolution/memory-distill/SKILL.md",
        "skills/6-orchestration/autoresearch/SKILL.md",
        "skills/6-orchestration/research-team/SKILL.md",
    ]

    for path in paths:
        assert text(path).count("```") % 2 == 0, path
