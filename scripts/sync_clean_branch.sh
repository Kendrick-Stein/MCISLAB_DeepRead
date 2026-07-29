#!/usr/bin/env bash
# 同步 clean-start 分支：从当前 HEAD 抽取 skill 框架（不含 Papers/Topics 等个人数据与任何密钥），
# 以 orphan 分支形式维护，供外部用户轻量克隆：
#   git clone -b clean-start --single-branch --depth 1 <repo-url>
#
# 用法：scripts/sync_clean_branch.sh [--no-push]
# 实现：git plumbing（read-tree/commit-tree），不切分支、不动工作区，可与其他 session 并行。
set -euo pipefail
cd "$(dirname "$0")/.."

BRANCH=clean-start
PUSH=1
[ "${1:-}" = "--no-push" ] && PUSH=0

# 白名单：skill 框架 + 运行依赖（只取 git 已跟踪内容，.env 等 ignored 文件天然不会进入）
INCLUDE=(
  AGENTS.md CLAUDE.md README.md .gitignore pyproject.toml skills-lock.json
  skills .claude scripts references Templates docs tests
  Workbench/config/team-config.json
)
# 黑名单（白名单目录内的例外）：
#   - references/bibtex-cache.bib     个人引用缓存
#   - .claude/skills/lark-*           指向 .agents/（未纳入）的 symlink，避免悬空
#   - .mcp.json / .codex 不在白名单：含 API key，严禁进入公开分支
is_excluded() {
  case "$1" in
    references/bibtex-cache.bib) return 0 ;;
    .claude/skills/lark-*)       return 0 ;;
  esac
  return 1
}

TMP_INDEX=$(mktemp)
trap 'rm -f "$TMP_INDEX"' EXIT
GIT_INDEX_FILE="$TMP_INDEX" git read-tree --empty

# 从 HEAD 抽取白名单路径，写入临时 index
git ls-tree -r HEAD -- "${INCLUDE[@]}" | while IFS=$'\t' read -r meta path; do
  is_excluded "$path" && continue
  mode=${meta%% *}
  sha=${meta##* }
  printf '%s %s 0\t%s\n' "$mode" "$sha" "$path"
done | GIT_INDEX_FILE="$TMP_INDEX" git update-index --index-info

TREE=$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)

# 防泄漏闸门：任何 blob 里出现疑似 key 直接拒绝生成
if git grep -lIiE '(api[_-]?key|secret|token)["'"'"']?\s*[:=]\s*["'"'"'][A-Za-z0-9]{16,}' "$TREE" -- . >/dev/null 2>&1; then
  echo "ERROR: 检测到疑似密钥，拒绝同步。检查：" >&2
  git grep -lIiE '(api[_-]?key|secret|token)["'"'"']?\s*[:=]\s*["'"'"'][A-Za-z0-9]{16,}' "$TREE" -- . >&2
  exit 1
fi

PARENT=$(git rev-parse -q --verify "refs/heads/$BRANCH" || true)
if [ -n "$PARENT" ] && [ "$(git rev-parse "$PARENT^{tree}")" = "$TREE" ]; then
  echo "$BRANCH 已是最新（tree 无变化）"
else
  MSG="sync: skill framework from main@$(git rev-parse --short HEAD)"
  COMMIT=$(git commit-tree "$TREE" ${PARENT:+-p "$PARENT"} -m "$MSG")
  git update-ref "refs/heads/$BRANCH" "$COMMIT"
  echo "$BRANCH -> $(git rev-parse --short "$COMMIT")（$(git ls-tree -r "$TREE" | wc -l | tr -d ' ') files）"
fi

if [ "$PUSH" = 1 ]; then
  git push origin "$BRANCH"
fi
