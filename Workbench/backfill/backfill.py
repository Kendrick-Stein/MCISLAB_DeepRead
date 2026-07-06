#!/usr/bin/env python3
"""venue 回填驱动（两阶段，可断点续跑）。

phase download: 串行温和下载 PDF→提取文本到 cache/。CVF 优先从 arxiv 取（绕开被封的 thecvf），
                无 arxiv 才温和访问 thecvf（指数退避）。journal 直接 arxiv。
phase analyze:  对已缓存文本并行跑 codex exec 生成 Papers/ 笔记。

Usage:
  python3 backfill.py download [--limit N]
  python3 backfill.py analyze  [--limit N] [--concurrency C]
"""
import argparse, difflib, json, os, re, subprocess, sys, threading, time, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WL = REPO / "Workbench/backfill/worklist_final.json"
CACHE = REPO / "Workbench/backfill/cache"
LOG = REPO / "Workbench/backfill/run.log"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
CACHE.mkdir(parents=True, exist_ok=True)
_lock = threading.Lock()


def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, file=sys.stderr, flush=True)
    with _lock, open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load(): return json.loads(WL.read_text(encoding="utf-8"))
def save(wl):
    with _lock:
        WL.write_text(json.dumps(wl, ensure_ascii=False, indent=1), encoding="utf-8")


def norm(t): return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


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
    title = p["title"]; head = title.split(":")[0]
    if ":" in title and len(head.split()) <= 3 and any(c.isupper() for c in head[1:]):
        slug = re.sub(r"[^A-Za-z0-9]", "", head)
    else:
        slug = "".join(w[:1].upper() + w[1:] for w in re.findall(r"[A-Za-z0-9]+", title)[:3])
    return f"Papers/{yymm}-{(slug[:26] or 'Paper')}.md"


def arxiv_pdf_by_title(title):
    """用 arxiv API 按标题找 arxiv 版（绕开 thecvf）。返回 pdf url 或 ''。"""
    q = urllib.request.quote(f'ti:"{title[:120]}"')
    url = f"http://export.arxiv.org/api/query?search_query={q}&max_results=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            root = ET.fromstring(r.read().decode())
    except Exception:
        return ""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    e = root.find("a:entry", ns)
    if e is None:
        return ""
    t = e.find("a:title", ns)
    if t is None or t.text is None:
        return ""
    if difflib.SequenceMatcher(None, norm(title), norm(t.text)).ratio() < 0.85:
        return ""
    idel = e.find("a:id", ns)
    m = re.search(r"abs/([\d.]+)", idel.text if idel is not None else "")
    return f"https://arxiv.org/pdf/{m.group(1)}" if m else ""


def fetch_pdf(url, dest, tries=3):
    for k in range(tries):
        subprocess.run(["curl", "-sL", "--max-time", "120", "-A", UA, "-o", dest, url],
                       capture_output=True)
        if os.path.exists(dest) and os.path.getsize(dest) > 20000:
            return True
        time.sleep(5 * (3 ** k))  # 5s,15s,45s 退避
    return False


def download_one(idx, p):
    txt = CACHE / f"{idx}.txt"
    if txt.exists() and txt.stat().st_size > 1000:
        return "cached"
    if (REPO / make_filename(p)).exists():
        return "skip-exists"
    # 选下载源：journal 用 arxiv；cvf 先试 arxiv，再退 thecvf
    url, via = p["fulltext"], "direct"
    if p["source"].startswith("cvf"):
        ax = arxiv_pdf_by_title(p["title"]); time.sleep(3)
        if ax:
            url, via = ax, "arxiv"
    pdf = CACHE / f"{idx}.pdf"
    ok = fetch_pdf(url, str(pdf))
    if not ok:
        return "dl-fail"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], capture_output=True)
    pdf.unlink(missing_ok=True)
    if txt.exists() and txt.stat().st_size > 1000:
        return f"ok-{via}"
    return "extract-fail"


def build_prompt(p, txt_path, fn):
    return f"""Write a Chinese research-paper digest note into this Obsidian research vault, strictly following the repo's conventions. Ground ONLY in the paper's actual content; do not invent results.

Paper title (approx): "{p['title']}"
Venue: {venue_label(p)}
Paper page: {p.get('page','')}
The COMPLETE paper text is already extracted at: {txt_path} — read it first.

Do exactly this:
1. Read {txt_path} (the full paper). Get exact title + authors + affiliations from the top.
2. Read and strictly follow: Templates/Paper.md (fill EVERY section per its %% %% guidance), references/tags.md (1-3 tags, most-relevant first), skills/1-literature/paper-digest/SKILL.md (Steps, Guard, grounding rules).
3. Write the note to EXACTLY: {fn}  (if it already exists, STOP and write nothing).
   frontmatter: title (quoted), authors [], institute [], date_publish, venue: "{venue_label(p)}", tags [], url: "{p.get('page','')}", arxiv_id (if the paper has an arXiv version — read it from the PDF header like 'arXiv:2503.18065', else leave empty), doi (if present in the paper, else empty), code (if mentioned), rating (1-5 integer by quality + relevance to GUI-agent / VLM / agentic / embodied research), date_added: 2026-06-26.
4. Chinese prose; keep English technical terms. Honest & evidence-driven — separate 已知/推测/不知道, surface ablations / failure cases / baselines / limitations. Summary <= 3 sentences. "Key Results" MUST cite concrete numbers + benchmark names. Include the Mind Map mermaid block.
5. Verify YAML frontmatter: any value with a colon (title, venue, url) must be double-quoted.

Follow Templates/Paper.md and paper-digest SKILL for note CONTENT and format, BUT do NOT run any Bash scripts (no cite_key / bibtex / assign scripts) — only write the single note file. Citation keys are assigned in a separate batch step.
IMPORTANT: Write a normal standalone paper note. Do NOT mention the extraction file path, target filename, or these instructions in the note body.
If the paper is clearly OFF-TOPIC for GUI-agent/VLM/agentic/embodied research, write nothing and report 'SKIP: off-topic'.
Report: created file path + one-sentence contribution."""


def analyze_one(idx, p):
    fn = make_filename(p)
    if (REPO / fn).exists():
        return idx, "skipped-exists", fn
    txt = CACHE / f"{idx}.txt"
    if not txt.exists():
        return idx, "no-cache", fn
    msg = f"/tmp/msg_{idx}.txt"
    try:
        subprocess.run(["codex", "exec", "-s", "workspace-write", "--add-dir", str(CACHE),
                        "--skip-git-repo-check", "-o", msg, build_prompt(p, str(txt), fn)],
                       cwd=str(REPO), capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return idx, "failed-timeout", fn
    if (REPO / fn).exists() and (REPO / fn).stat().st_size > 600:
        return idx, "done", fn
    last = Path(msg).read_text(encoding="utf-8") if os.path.exists(msg) else ""
    if "SKIP" in last.upper() or "off-topic" in last.lower():
        return idx, "skipped-offtopic", fn
    if any(w in last for w in ["已存在", "去重", "already exist"]):
        return idx, "skipped-dup", fn
    return idx, "failed-codex", fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["download", "analyze"])
    ap.add_argument("--limit", type=int, default=9999)
    ap.add_argument("--concurrency", type=int, default=4)
    a = ap.parse_args()
    wl = load()

    if a.phase == "download":
        todo = [(i, p) for i, p in enumerate(wl) if p.get("status") == "pending"
                and not p.get("cached")][: a.limit]
        log(f"=== download start: {len(todo)} papers (serial, arxiv-preferred) ===")
        res = {}
        for i, p in todo:
            r = download_one(i, p)
            if r.startswith("ok") or r == "cached":
                p["cached"] = True
            elif r == "skip-exists":
                p["status"] = "skipped-exists"
            elif r == "dl-fail":
                p["dl_fail"] = p.get("dl_fail", 0) + 1
            save(wl)
            res[r] = res.get(r, 0) + 1
            log(f"  [{r:12}] {p['title'][:46]}")
            time.sleep(4)  # 对服务器友好
        log(f"=== download done: {res} ===")
        print(json.dumps(res, ensure_ascii=False))

    else:  # analyze
        todo = [(i, p) for i, p in enumerate(wl) if p.get("status") == "pending"
                and p.get("cached")][: a.limit]
        log(f"=== analyze start: {len(todo)} papers, concurrency={a.concurrency} ===")
        res = {}
        with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
            futs = [ex.submit(analyze_one, i, p) for i, p in todo]
            for f in as_completed(futs):
                idx, status, fn = f.result()
                wl[idx]["status"] = status; wl[idx]["filename"] = fn
                save(wl)
                res[status] = res.get(status, 0) + 1
                log(f"  [{status:16}] {fn} | {wl[idx]['title'][:42]}")
        log(f"=== analyze done: {res} ===")
        print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
