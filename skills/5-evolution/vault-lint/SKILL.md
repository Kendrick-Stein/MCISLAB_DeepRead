---
name: vault-lint
description: >
  当 Supervisor 说"体检一下 vault""检查笔记质量""跑一下 lint"，或 autoresearch 例行触发
  （距上次 lint >7 天、或本周批量 digest ≥10 篇、或建站前）时，对 vault 内容目录跑机械
  质量检查：frontmatter YAML、cite_key 完整性、wikilink 失链、abstract-only 笔记、
  Quartz 建站隐患（字面 $、引号嵌套）、模板残留。
argument-hint: "[--build 附带建站冒烟] [--check yaml/cite-key/wikilink/abstract/dollar/placeholder]"
allowed-tools: Read, Edit, Glob, Grep, Bash
---

# Vault Lint — 把踩过的坑固化成机械检查

## Purpose

vault 里反复出现过几类机械故障（见 Workbench/memory）：cite_key 留空 `""` 被
assign_cite_keys 静默跳过导致丢引用身份、abstract-only 低质笔记滞留、frontmatter 引号/
字面 `$` 弄挂 Quartz build、改名后 wikilink 失链。过去都是事后手工修——本 skill 用
`vault_lint.py` 把它们变成可定期跑的机械检查 + 分类处置流程，问题在积累前被清掉。

## Steps

### Step 1：跑检查

```bash
python3 skills/5-evolution/vault-lint/vault_lint.py          # 常规
python3 skills/5-evolution/vault-lint/vault_lint.py --build  # 建站前（附 quartz build 冒烟）
```

退出码 0 = 无 ERROR。输出按检查类分组（ERROR 必须处置，WARN 需 triage）。

### Step 2：分类处置

| 检查类 | 处置方式 |
|:--|:--|
| `[yaml]` | 机械修：字段值加引号 / string 改 list。修完重跑确认 |
| `[cite-key]` | **只经脚本修**：先按提示删 `""` 引号陷阱（`sed 's/^cite_key: ""$/cite_key:/'`），再跑 `assign_cite_keys.py`；批量新分配后补跑 `fetch_bibtex.py --offline` 或分批在线抓取（注意 arXiv 限速）。禁止手编 cite_key |
| `[wikilink]` | 逐条 triage：目标改名/合并 → 更新链接指向新名（如 merged survey 指向 canonical）；目标确实不存在 → 修正或删除链接。survey 正文出现 memory slug 等内部痕迹链接 = 违反写作基线第 9 条，一并清除 |
| `[abstract]` | 按既定规则：**无入链 → 列删除候选清单给 Supervisor 确认**（不直接删）；**有入链 → 进 queue 重抓全文 re-digest**（arxiv/html → ar5iv 顺序） |
| `[dollar]` | 逐文件甄别：散文里 $+数字恒为货币 → 整行转义 `\$`；Papers 数学货币混杂 → 逐处判断，数学公式保留 |
| `[placeholder]` | 补写或删除残留 `%%` 注释 / `[TODO]`；abstract-only 导致的空节按 `[abstract]` 规则走 |

### Step 3：复跑验证

处置完成后重跑 Step 1，确认 ERROR = 0；仍留的 WARN 必须每条有 triage 结论
（"保留，因为…"）。

### Step 4：记录

追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] vault-lint
- **scan**: N files | E errors / W warnings
- **fixed**: <cite-key N 篇 / wikilink N 处 / yaml N 处 / …>
- **pending**: <删除候选 N 篇待 Supervisor 确认 / re-digest 入 queue N 篇 / 无>
- **status**: clean / residual-warns
```

## Guard

- **只修机械问题，不改内容语义**：lint 不重写笔记正文、不调整结论、不动 rating。
- **cite_key 修复只经 `assign_cite_keys.py`**——不手编 key（key 一旦写入永久冻结，
  手编会破坏碰撞解析）。
- **abstract-only 笔记不直接删**：删除候选列清单给 Supervisor / 进 queue review，
  确认后才删；有入链的一律走重抓全文，不删。
- **$ 转义前必须甄别**：Papers 数学与货币混杂，不做整目录盲替换。
- 修复用 Edit / 既有脚本；不引入新的批量改写脚本。

## Verify

- [ ] `vault_lint.py` 复跑退出码 0（ERROR = 0）
- [ ] 残余 WARN 每条有 triage 结论记录在日志
- [ ] cite-key 修复后抽查 2-3 篇：frontmatter `cite_key` 非空且未改动既有 key
- [ ] 删除候选/re-digest 清单已交 Supervisor 或入 queue（未擅自删除）
- [ ] 日志 entry 四项齐全

## Examples

`/vault-lint` → 1014 files，174 ERROR（163 篇 `""` 陷阱 + 11 篇缺失）→ sed 清陷阱 +
assign_cite_keys 批量分配 → 复跑 0 ERROR，18 WARN（16 失链逐条 triage + 2 模板残留补写）。
