#!/usr/bin/env python3
"""
Small Lexmount WebFetch CLI for paper retrieval fallbacks.

Examples:
    python3 scripts/lexmount_fetch.py extract https://arxiv.org/html/2604.06126
    python3 scripts/lexmount_fetch.py dump https://arxiv.org/html/2604.06126 --engine lightmount_domstable
"""

import argparse
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://webfetch.lexmount.com"


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or Path.cwd() / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("LEXMOUNT_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("LEXMOUNT_API_KEY is required. Put it in the environment or ignored .env file.")
    return api_key


def base_url() -> str:
    # 优先 LEXMOUNT_WEBFETCH_BASE_URL；其次 LEXMOUNT_BASE_URL（api.lexmount.cn/.com，
    # 与 .env 对齐）；都缺才落回旧默认主机。
    url = os.environ.get("LEXMOUNT_WEBFETCH_BASE_URL", "").strip() or \
        os.environ.get("LEXMOUNT_BASE_URL", "").strip() or DEFAULT_BASE_URL
    return url.rstrip("/")


def post_json(path: str, payload: dict, timeout_ms: int = 30000) -> dict:
    api_key = require_api_key()
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
        "User-Agent": "read-paper-machine/lexmount-fetch",
    }
    # api.lexmount.* 端点要求 project id 头；旧 webfetch 主机忽略该头。
    project_id = os.environ.get("LEXMOUNT_PROJECT_ID", "").strip()
    if project_id:
        headers["x-project-id"] = project_id
    req = Request(
        f"{base_url()}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urlopen(req, timeout=max(timeout_ms / 1000 + 10, 30)) as resp:
        raw = resp.read().decode("utf-8")

    data = json.loads(raw)
    if data.get("error"):
        raise RuntimeError(f"Lexmount API error: {data['error']}")
    return data


def extract(
    url: str,
    timeout_ms: int = 30000,
    include_steps: bool = False,
    include_raw_dom: bool = False,
) -> dict:
    payload = {
        "extract": {"url": url},
        "workflow": {
            "match_timeout_ms": timeout_ms,
            "generate_timeout_ms": timeout_ms,
            "extract_timeout_ms": timeout_ms,
        },
        "trace": {
            "include_steps": include_steps,
            "include_raw_dom": include_raw_dom,
        },
    }
    return post_json("/v1/extract", payload, timeout_ms=timeout_ms)


def dump_dom(
    url: str,
    engine_preference: str = "lightmount_dcl",
    timeout_ms: int = 30000,
    filter_scripts_styles: bool = False,
) -> dict:
    payload = {
        "url": url,
        "options": {
            "engine_preference": engine_preference,
            "timeout_ms": timeout_ms,
            "filter_scripts_styles": filter_scripts_styles,
        },
    }
    return post_json("/v1/dom/dump", payload, timeout_ms=timeout_ms)


def html_to_text(raw_html: str) -> str:
    text = (raw_html or "").strip()
    if not text:
        return ""

    pre_match = re.search(r"<pre[^>]*>(.*?)</pre>", text, flags=re.IGNORECASE | re.DOTALL)
    if pre_match:
        return html_lib.unescape(pre_match.group(1)).strip()

    if re.search(r"<[^>]+>", text):
        text = re.sub(r"(?is)<(script|style).*?</\1>", "", text)
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</(p|div|li|tr|h[1-6])>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = html_lib.unescape(text)

    return text.strip()


def format_extract(data: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)

    result = data.get("result", {})
    main_text = result.get("main_text") or result.get("description") or ""
    if output_format == "text":
        return main_text.strip()

    lines = []
    title = result.get("title") or "Lexmount Extract"
    lines.append(f"# {title}")
    for key in ("final_url", "status_code", "author", "publish_time", "language", "engine", "template_id", "dom_id"):
        value = result.get(key)
        if value not in (None, ""):
            lines.append(f"- {key}: {value}")
    if main_text:
        lines.extend(["", "## Main Text", "", main_text.strip()])
    links = result.get("links") or []
    if links:
        lines.extend(["", "## Links"])
        for link in links[:100]:
            if isinstance(link, dict):
                href = link.get("href") or link.get("url") or ""
                text = link.get("text") or href
                lines.append(f"- {text}: {href}")
            else:
                lines.append(f"- {link}")
    return "\n".join(lines).strip()


def format_dump(data: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    if output_format == "html":
        return data.get("html", "")
    return html_to_text(data.get("html", ""))


def write_output(text: str, output_path: str | None) -> None:
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + ("\n" if text and not text.endswith("\n") else ""), encoding="utf-8")
    else:
        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch pages through Lexmount WebFetch.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Call POST /v1/extract.")
    extract_parser.add_argument("url")
    extract_parser.add_argument("--timeout-ms", type=int, default=30000)
    extract_parser.add_argument("--include-steps", action="store_true")
    extract_parser.add_argument("--include-raw-dom", action="store_true")
    extract_parser.add_argument("--format", choices=("markdown", "text", "json"), default="markdown")
    extract_parser.add_argument("--output", "-o")

    dump_parser = subparsers.add_parser("dump", help="Call POST /v1/dom/dump.")
    dump_parser.add_argument("url")
    dump_parser.add_argument("--engine", default="lightmount_dcl")
    dump_parser.add_argument("--timeout-ms", type=int, default=30000)
    dump_parser.add_argument("--filter-scripts-styles", action="store_true")
    dump_parser.add_argument("--format", choices=("text", "html", "json"), default="text")
    dump_parser.add_argument("--output", "-o")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "extract":
            data = extract(
                args.url,
                timeout_ms=args.timeout_ms,
                include_steps=args.include_steps,
                include_raw_dom=args.include_raw_dom,
            )
            write_output(format_extract(data, args.format), args.output)
            return 0

        data = dump_dom(
            args.url,
            engine_preference=args.engine,
            timeout_ms=args.timeout_ms,
            filter_scripts_styles=args.filter_scripts_styles,
        )
        write_output(format_dump(data, args.format), args.output)
        return 0
    except Exception as exc:
        print(f"lexmount_fetch: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
