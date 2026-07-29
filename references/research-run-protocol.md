# Research Run Protocol

`Workbench/runs/{run_id}.json` is the resumable state for multi-stage research. It is coordination state, not a research evidence source.

## Required schema

```json
{
  "version": 1,
  "run_id": "survey-gui-agent-20260723-0930",
  "workflow": "literature-survey",
  "topic": "GUI Agent",
  "status": "in_progress",
  "stage": "prepare",
  "budget": {
    "max_papers": 20,
    "max_search_queries": 10,
    "max_wall_minutes": 90
  },
  "counts": {
    "candidates": 0,
    "prepared": 0,
    "committed": 0,
    "reviewed": 0,
    "source_verified_claims": 0,
    "downgraded_claims": 0,
    "disputed_claims": 0,
    "failed": 0
  },
  "artifacts": [],
  "failed_items": [],
  "unresolved_gaps": [],
  "checkpoint_at": "2026-07-23T09:30:00"
}
```

Allowed `status`: `in_progress`, `partial`, `completed`, `failed`.

Recommended stage order: `discover` → `triage` → `prepare` → `source_verify` → `commit` → `cross_paper_audit` → `gap` → `synthesize` → `done`. Workflows may skip irrelevant stages but must not relabel completed stages as unfinished.

## Write and resume rules

1. Coordinator is the sole manifest writer. Parallel workers return artifact envelopes and never edit the manifest.
2. Update via temporary file + atomic rename. Set `checkpoint_at` on every stage transition and every configured artifact batch.
3. Do not store secrets, raw chain-of-thought, full fetched documents, or long agent transcripts. Store paths, compact error messages, claim counts, and evidence boundaries.
4. `partial` is a valid deliverable: preserve committed artifacts and unresolved gaps. A resumed run verifies that artifact paths still exist, then continues from the first incomplete stage.
5. Budget exhaustion stops new dispatch, not safe commit. Finish the current coordinator write, emit partial synthesis when possible, and record what remains.
6. Run manifests are audit/coordination pointers. They never count as independent evidence in `memory-distill`.
