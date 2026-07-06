#!/usr/bin/env python3
"""venue 回填驱动：从 worklist_final.json 取 pending 论文 → 下载/提取 PDF → codex exec 生成笔记。

可断点续跑（状态写回 worklist），限并发，预下载+预提取后只让 codex 读文本写笔记。

Usage:
  python3 run_backfill.py --limit 1                 # 测试 1 篇
  python3 run_backfill.py --limit 20 --concurrency 4
"""
import argparse, json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKLIST = REPO / "Workbench/backfill/worklist_final.json"
LOG = REPO / "Workbench/backfill/run.log"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_lock = threading.Lock()


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, file=sys.stderr, flush=True)
    with _lock:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def load(): return json.loads(WORKLIST.read_text(encoding="utf-8"))


def save(wl):
    with _lock:
        WORKLIST.write_text(json.dumps(wl, ensure_ascii=False, indent=1), encoding="utf-8")


def venue_label(p):
    s = p["source"]
    if s.startswith("cvf"):
        m = re.search(r"(20\d\d)", s)
        conf = "CVPR" if "CVPR" in s else ("ICCV" if "ICCV" in s else "WACV")
        return f"{conf} {m.group(1)}"
    return p.get("venue", "")


def make_filename(p):
    s = p["source"]
    if s.startswith("cvf"):
        yr = re.search(r"(20\d\d)", s).group(1)
        conf = "CVPR" if "CVPR" in s else ("ICCV" if "ICCV" in s else "WACV")
        mm = {"CVPR": "06", "ICCV": "10", "WACV": "01"}[conf]
        yymm = yr[2:] + mm
    else:
        am = re.search(r"/(\d{2})(\d{2})\.\d+", p.get("fulltext", ""))
        yymm = (am.group(1) + am.group(2)) if am else "2500"
    title = p["title"]
    head = title.split(":")[0]
    if ":" in title and len(head.split()) <= 3 and any(c.isupper() for c in head[1:]):
        slug = re.sub(r"[^A-Za-z0-9]", "", head)
    else:
        words = re.findall(r"[A-Za-z0-9]+", title)[:3]
        slug = "".join(w[:1].upper() + w[1:] for w in words)
    slug = (slug[:26] or "Paper")
    return f"Papers/{yymm}-{slug}.md"


def build_prompt(p, txt_path, filename):
    return f"""Write a Chinese research-paper digest note into this Obsidian research vault, strictly following the repo's conventions. Ground ONLY in the paper's actual content; do not invent results.

Paper title (approx): "{p['title']}"
Venue: {venue_label(p)}
Paper page: {p.get('page','')}
The COMPLETE paper text is already extracted at: {txt_path} — read it first.

Do exactly this:
1. Read {txt_path} (the full paper). Get exact title + authors + affiliations from the top.
2. Read and strictly follow: Templates/Paper.md (fill EVERY section per its %% %% guidance), references/tags.md (pick 1-3 tags from the taxonomy, most-relevant first), skills/1-literature/paper-digest/SKILL.md (Steps, Guard, grounding rules).
3. Write the note to EXACTLY: {filename}  (if it already exists, STOP and write nothing).
   frontmatter: title (quoted), authors [list], institute [list], date_publish, venue: "{venue_label(p)}", tags [], url: "{p.get('page','')}", code (if mentioned), rating (1-5 integer by quality + relevance to GUI-agent / VLM / agentic / embodied-AI research), date_added: 2026-06-26.
4. Writing rules: Chinese prose; keep English technical terms (model / method / benchmark names) untranslated. Honest & evidence-driven — separate 已知/推测/不知道, no overclaiming, surface ablations / failure cases / baselines / limitations. Summary ≤ 3 sentences. "Key Results" MUST cite concrete numbers + benchmark names. Include the Mind Map mermaid block.
5. Verify YAML frontmatter: any value containing a colon (title, venue, url) must be double-quoted; fix if not.

IMPORTANT: Write the note as a normal standalone paper note. Do NOT mention the extraction text file path, the target filename, "目标文件名", these instructions, or any pipeline mechanics inside the note body.

Report: the created file path + a one-sentence core contribution. If the paper is clearly OFF-TOPIC for GUI-agent/VLM/agentic/embodied research, instead write nothing and report 'SKIP: off-topic'.
"""


def process(idx, p):
    fn = make_filename(p)
    if (REPO / fn).exists():
        return idx, "skipped-exists", fn
    pdf = f"/tmp/bf_{idx}.pdf"
    txt = f"/tmp/bf_{idx}.txt"
    # 下载
    r = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, "-o", pdf, p["fulltext"]],
                       capture_output=True)
    if not os.path.exists(pdf) or os.path.getsize(pdf) < 20000:
        return idx, "failed-download", fn
    # 提取
    subprocess.run(["pdftotext", "-layout", pdf, txt], capture_output=True)
    if not os.path.exists(txt) or os.path.getsize(txt) < 1000:
        return idx, "failed-extract", fn
    # codex
    prompt = build_prompt(p, txt, fn)
    msg = f"/tmp/bf_{idx}_msg.txt"
    try:
        cp = subprocess.run(
            ["codex", "exec", "-s", "workspace-write", "--add-dir", "/tmp",
             "--skip-git-repo-check", "-o", msg, prompt],
            cwd=str(REPO), capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return idx, "failed-timeout", fn
    if (REPO / fn).exists() and (REPO / fn).stat().st_size > 600:
        return idx, "done", fn
    # 可能 codex 判定 off-topic
    last = Path(msg).read_text(encoding="utf-8") if os.path.exists(msg) else ""
    if "SKIP" in last.upper():
        return idx, "skipped-offtopic", fn
    return idx, "failed-codex", fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=1)
    args = ap.parse_args()

    wl = load()
    pending = [(i, p) for i, p in enumerate(wl) if p.get("status") == "pending"]
    batch = pending[: args.limit]
    log(f"=== backfill start: {len(batch)} papers, concurrency={args.concurrency} ===")

    results = {}
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(process, i, p): i for i, p in batch}
        for fut in as_completed(futs):
            idx, status, fn = fut.result()
            wl[idx]["status"] = status
            wl[idx]["filename"] = fn
            save(wl)
            results[status] = results.get(status, 0) + 1
            log(f"  [{status:16}] {fn}  | {wl[idx]['title'][:50]}")

    log(f"=== done: {results} ===")
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
