#!/usr/bin/env bash
# ReadPaperMachine 初始化向导。
#   scripts/init.sh            交互设置研究兴趣（写 team-config.json + agenda Mission 骨架）
#   scripts/init.sh --fresh    先清空示例个人数据再进入向导
#   --yes                      非交互（--fresh 不再确认；向导用占位默认值，供测试）
set -euo pipefail
cd "$(dirname "$0")/.."

FRESH=0; YES=0
for arg in "$@"; do
  case "$arg" in
    --fresh) FRESH=1 ;;
    --yes) YES=1 ;;
    *) echo "unknown arg: $arg"; exit 2 ;;
  esac
done

if [ "$FRESH" = 1 ]; then
  echo "将清空个人数据: Papers/ Topics/ Ideas/ Reports/ Meetings/ Experiments/ News/ Projects/ DomainMaps/ 及 Workbench 状态"
  echo "框架保留: skills/ references/ Templates/ docs/ scripts/ .claude/ CLAUDE.md"
  if [ "$YES" != 1 ]; then
    read -r -p "确认？建议先 git commit 当前状态 [y/N] " ok
    [ "$ok" = "y" ] || { echo "已取消"; exit 1; }
  fi
  for d in Papers Topics Ideas Reports Meetings Experiments News Projects DomainMaps; do
    [ -d "$d" ] && find "$d" -mindepth 1 -not -name "_index.md" -delete
    mkdir -p "$d"
    [ -f "$d/_index.md" ] || printf -- '---\ntitle: %s Index\ntags: [index]\n---\n\n# %s\n' "$d" "$d" > "$d/_index.md"
  done
  rm -rf Workbench/logs Workbench/daily Workbench/evolution Workbench/backfill Workbench/runs
  mkdir -p Workbench/logs Workbench/daily Workbench/memory Workbench/config Workbench/runs
  : > Workbench/runs/.gitkeep
  printf '{\n  "queue": [],\n  "version": 2,\n  "updated_at": "%s",\n  "settings": {}\n}\n' "$(date +%F)" > Workbench/queue.json
  rm -f Workbench/survey-updates.json Workbench/survey-updates.json.bak Workbench/redigest-manifest.md
  : > Workbench/memory/insights.md; : > Workbench/memory/patterns.md
  echo "个人数据已清空。"
fi

if [ "$YES" = 1 ]; then
  DIRECTIONS="My Research Topic"; KEYWORDS="my topic, my method"
else
  read -r -p "研究方向（逗号分隔，如: GUI Agent, VLM）: " DIRECTIONS
  read -r -p "打分关键词（逗号分隔，如: gui agent, computer use, vlm）: " KEYWORDS
fi

python3 - "$DIRECTIONS" "$KEYWORDS" "$FRESH" <<'EOF'
import json, sys, datetime
from pathlib import Path
directions = [d.strip() for d in sys.argv[1].split(",") if d.strip()]
keywords = [k.strip() for k in sys.argv[2].split(",") if k.strip()]
fresh = sys.argv[3] == "1"
cfg_path = Path("Workbench/config/team-config.json")
cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
cfg["interests"] = [{"name": d, "keywords": keywords} for d in directions] or cfg.get("interests", [])
digest_defaults = {
    "parallel_limit": 4,
    "prepare_parallel_limit": 2,
    "review_parallel_limit": 2,
    "timeout_minutes": 12,
    "retry_limit": 2,
}
digest = cfg.setdefault("digest", {})
for key, value in digest_defaults.items():
    digest.setdefault(key, value)
orchestration_defaults = {
    "checkpoint_every": 3,
    "max_papers_per_run": 20,
    "max_search_queries": 10,
    "post_verification_queries": 3,
    "post_verification_loops": 1,
    "synthesis_min_committed": 3,
    "max_wall_minutes": 90,
}
orchestration = cfg.setdefault("orchestration", {})
for key, value in orchestration_defaults.items():
    orchestration.setdefault(key, value)
role_defaults = {
    "finder": {"tier": "cheap-fast"},
    "digest": {"tier": "balanced"},
    "verifier": {"tier": "strong", "require_different_agent": True, "hide_finder_reasoning": True},
    "judge": {"tier": "strongest-available", "trigger": "disputed-high-impact-only"},
    "synthesis": {"tier": "strong"},
}
model_policy = cfg.setdefault("model_policy", {})
for role, policy in role_defaults.items():
    model_policy.setdefault(role, policy)
cfg.setdefault("news", {"sources": [], "days": 3, "min_score": 1, "top_n": 20})
cfg_path.parent.mkdir(parents=True, exist_ok=True)
cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

agenda = Path("Workbench/agenda.md")
if not agenda.exists() or fresh or not agenda.read_text().strip():
    today = datetime.date.today().isoformat()
    agenda.write_text(f'''---
last_updated: "{today}"
updated_by: init
---

## Mission

（用 1-3 句描述长期研究目标；方向: {", ".join(directions)}）

---

## Active Directions

（由 agenda-evolve / Supervisor 逐步填充）

## Paused Directions

（暂无）

## Discussion Topics

（暂无）
''')
print("team-config.json / agenda.md 已就绪")
EOF

python3 scripts/sync_skills.py || true
echo "完成。下一步: 在 Claude Code 中运行 /daily-papers 或 /autoresearch"
