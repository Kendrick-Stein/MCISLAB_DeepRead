# Memory Protocol

This document defines how MindFlow stores, organizes, and promotes research knowledge. The memory system transforms raw observations into structured, reusable insights.

---

## Directory Structure

All persistent memory lives under `Workbench/memory/` as plain Markdown files.

```
Workbench/
  memory/
    patterns.md            # Cross-paper or cross-experiment patterns (not yet validated)
    insights.md            # Discovered insights (provisional -> validated)
    effective-methods.md   # Proven experiment and analysis strategies
    failed-directions.md   # Abandoned research directions and the reasons why
  logs/                    # Raw session logs (Level 0 input to memory)
  evolution/
    changelog.md           # Record of every DomainMaps update
```

| File | Purpose | Key Fields |
|---|---|---|
| `patterns.md` | Early-stage observations that recur across sources; feeds the promotion pipeline | observation, occurrences, evidence, source_ids, confidence, needs_verification |
| `insights.md` | Curated claims with canonical evidence identity and confidence tracking | claim, evidence, source_ids, audit_logs, confidence, source, impact, status, status_history |
| `effective-methods.md` | Strategies that worked, with context and caveats | context, method, evidence, pitfalls |
| `failed-directions.md` | What was tried and why it was abandoned; prevents re-exploring dead ends | original_hypothesis, evidence_against, lesson, related_directions |

---

## Entry Format

All memory files use the same heading-and-bullet structure. Entries are **append-only** — never edit past entries; add a new entry to supersede.

```markdown
### [YYYY-MM-DD] Entry title

- **field_1**: value
- **field_2**: value
- ...
```

Each file's specific fields are listed in the table above. Common rules:
- Use Obsidian `[[wikilinks]]` for all evidence references.
- Store canonical `source_ids` beside wikilinks. Logs are audit pointers, not independent evidence.
- Claims and hypotheses must be falsifiable and specific.
- `confidence` in `patterns.md` is capped at `medium` — validated patterns belong in `insights.md`.

---

## Insight Promotion Hierarchy

Knowledge is promoted upward through five levels as evidence accumulates.

```
Level 4  Domain Map           DomainMaps/{Name}.md
         Stable, integrated knowledge
              |  Human approves pending review_insight task
Level 3  Validated Insight    insights.md, status: validated
              |  >=3 canonical sources + quality/contradiction gate
Level 2  Provisional Insight  insights.md, status: provisional
              |  >=2 canonical sources support
Level 1  Pattern              patterns.md
              |  memory-distill extracts from logs
Level 0  Raw Log              Workbench/logs/
```

### Promotion Rules

| Transition | Trigger | Who |
|---|---|---|
| L0 -> L1 | `memory-distill` processes session logs and extracts recurring observations | Researcher (via skill) |
| L1 -> L2 | Pattern has >=2 unique canonical source_ids | Researcher (via skill) |
| L2 -> L3 | >=3 source_ids, source/experiment verification passes, and no unresolved contradiction | Researcher (via skill) |
| L3 -> L4 | `review_insight` is approved; no numeric threshold replaces Human judgment | Human |

**Independent-source rule**: identity is based on the underlying paper/experiment/dataset/code artifact, not date, agent, run, URL variant, or venue version. The same paper summarized on three dates remains one source. `source-verified` means the primary source contains the claim; it is not an independent replication.

---

## Update Rules

1. **Append-only**: Never edit or delete existing entries. To supersede, append a new entry with updated date.

2. **DomainMaps logging**: Every L4 promotion must be logged to `Workbench/evolution/changelog.md`:

   ```markdown
   ### [YYYY-MM-DD] Domain Map updated: <map name>
   - **added**: <insight title>
   - **source**: [[Workbench/memory/insights.md#<heading>]]
   - **promoted_by**: <skill name or "human">
   ```

3. **Supervisor writes**: Supervisor may write directly to any memory file at any time without restrictions.

4. **Conflict handling**: If a new insight contradicts an existing validated one, create a new `provisional` entry noting the contradiction. Do not modify the old entry.
