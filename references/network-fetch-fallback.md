# Network Fetch Fallback

When normal `WebSearch`, `WebFetch`, or direct Python `urlopen` calls stall or return incomplete paper content, use Lexmount WebFetch as a backup path.

## Secret Handling

- Never commit API keys or paste them into notes, logs, reports, or paper frontmatter.
- Read credentials from `LEXMOUNT_API_KEY`.
- Optional local setup: put `LEXMOUNT_API_KEY=...` in `.env`. This repository already ignores `.env`.
- Optional override: `LEXMOUNT_WEBFETCH_BASE_URL=https://webfetch.lexmount.com`.

## CLI

Use the local helper:

```bash
python3 scripts/lexmount_fetch.py extract "https://arxiv.org/html/2604.06126" --format markdown
python3 scripts/lexmount_fetch.py dump "https://arxiv.org/html/2604.06126" --engine lightmount_domstable --format text
python3 scripts/lexmount_fetch.py extract "https://huggingface.co/papers/2604.06126" --format markdown
```

## Fallback Order

1. Try the normal path first.
2. If the response is empty, stalls, or only contains abstract-level content, retry with Lexmount `extract`.
3. If `extract` is insufficient, retry with Lexmount `dump` and inspect the text or HTML.
4. If Lexmount also fails, record the failure explicitly and do not infer missing details.

## arXiv Full Text

For arXiv inputs, prefer full-text HTML over PDF when using a web extraction fallback:

1. `https://arxiv.org/html/<arxiv_id>`
2. `https://ar5iv.labs.arxiv.org/html/<arxiv_id>`
3. `https://arxiv.org/abs/<arxiv_id>` for metadata and abstract
4. PDF only when a local PDF reader or separate PDF extraction path is available

If only abstract is available, mark affected sections with `> [未获取全文，仅基于 abstract]`.

## HuggingFace

For HuggingFace Daily, Trending, papers, model, or dataset pages:

1. Direct API or normal page fetch remains the primary path.
2. If it stalls, use Lexmount `extract` on the public page or API endpoint.
3. For dynamic pages, use `dump --engine chrome_cdp` or `dump --engine lightmount_domstable`.

## Error Handling

- `401`: key missing or invalid.
- `422`: extraction/template issue; use `dump` to inspect actual fetched DOM.
- `502`: target fetch/render failed; retry later or try a different canonical URL.
- `500`: record URL and response, then fall back to abstract-only handling.
