#!/usr/bin/env python3
"""TikZ design-quality linter — ADVISORY metrics report.

Where `tikz-validator.py` catches *syntactic / geometric* bugs (micro-slope,
overflow, collision), this script reports *structural design* metrics so Claude
+ user can decide if the figure's complexity matches the paper's needs.

**This is intentionally NOT a hard gate by default.** Simple figures (Bayesian
nets, geometric diagrams, comparison figures) often need fewer elements than
the "rich" preset suggests, and forcing them into a complex template degrades
quality. The linter surfaces metrics; you decide.

Metrics reported:
  * element_count — total visual elements (nodes + draws + fills + foreach)
  * size_ratio — max/min node area ratio
  * hero_present — at least one node big enough to be visually dominant
  * line_type_count — distinct (color, dash, width) tuples
  * zone_count — fit-nodes + background-layer fills
  * embedded_viz_count — \\foreach loops with fill/plot bodies

Default mode (advisory):
  * All sub-threshold metrics → WARN (informative, not blocking)
  * Single hard ERROR: 8+ nodes with size_ratio < 1.5 (zero hierarchy on a
    complex figure — legitimately broken design that needs fixing)

Usage:
    python3 tikz-design-linter.py <file.tex> [--json] [--strict] [--type ...]

Exit code:
    0 = no issues
    1 = WARN — advisory only, figure can ship
    2 = ERROR — broken design (only triggered by the strict hierarchy gate or `--strict`)

`--strict` upgrades all WARN → ERROR for projects that want the historical
"max design ambition" enforcement.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


# ─── Thresholds (the "最低设计门槛") ──────────────────────────────────────

@dataclass(frozen=True)
class DesignThresholds:
    """Numeric gate for design ambition. Override per project if needed."""
    min_element_count: int = 30          # nodes + draws + fills + foreach iterations
    min_size_ratio: float = 3.0          # largest node area / smallest node area
    min_line_type_count: int = 3         # distinct (color, dash, width) tuples
    min_zone_count: int = 2              # fit-nodes or background-layer fills
    min_embedded_viz_count: int = 1      # \fill loops / heatmaps / bar charts
    min_hero_width_cm: float = 5.0       # at least one node ≥ 5cm wide
    min_hero_area_cm2: float = 12.0      # OR area ≥ 12 cm²


DEFAULTS = DesignThresholds()

# Diagram-type presets — relaxed thresholds for figure types that don't need
# the full "rich data-viz" treatment (sequence diagrams, simple flows, etc).
TYPE_PRESETS: dict[str, DesignThresholds] = {
    "rich": DEFAULTS,                                           # default
    "sequence": DesignThresholds(
        min_element_count=18, min_size_ratio=1.5,
        min_line_type_count=2, min_zone_count=1,
        min_embedded_viz_count=0, min_hero_width_cm=0.0,
        min_hero_area_cm2=0.0,
    ),
    "simple": DesignThresholds(
        min_element_count=20, min_size_ratio=2.0,
        min_line_type_count=2, min_zone_count=1,
        min_embedded_viz_count=0, min_hero_width_cm=4.0,
        min_hero_area_cm2=8.0,
    ),
}


# ─── Issue model ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Issue:
    level: str           # ERROR or WARN
    metric: str
    actual: float | int
    threshold: float | int
    message: str


@dataclass
class Metrics:
    element_count: int = 0
    node_count: int = 0
    draw_count: int = 0
    fill_count: int = 0
    foreach_iterations: int = 0
    distinct_node_areas: int = 0
    size_ratio: float = 0.0
    line_type_count: int = 0
    line_type_examples: list[str] = field(default_factory=list)
    zone_count: int = 0
    embedded_viz_count: int = 0
    hero_present: bool = False
    hero_max_width_cm: float = 0.0
    hero_max_area_cm2: float = 0.0


# ─── Regex patterns ──────────────────────────────────────────────────────

# Strip line comments (but preserve `\%` escapes — rare in figure code)
COMMENT_RE = re.compile(r'(?<!\\)%.*$', re.MULTILINE)

# Node with explicit minimum width/height (cm assumed)
NODE_OPTS_RE = re.compile(r'\\node\s*\[([^\]]*)\]')
MINWIDTH_RE = re.compile(r'minimum\s*width\s*=\s*([\d.]+)\s*cm')
MINHEIGHT_RE = re.compile(r'minimum\s*height\s*=\s*([\d.]+)\s*cm')
MINSIZE_RE = re.compile(r'minimum\s*size\s*=\s*([\d.]+)\s*cm')

# \draw with options — capture the option string
DRAW_OPTS_RE = re.compile(r'\\draw\s*\[([^\]]*)\]')

# \fill commands (often used for heatmap cells, bar chart bars, zone backgrounds)
FILL_RE = re.compile(r'\\fill\b')

# \foreach loop — count iterations from explicit list length
FOREACH_LIST_RE = re.compile(r'\\foreach\b[^{]+\{([^}]+)\}')

# fit=(...) nodes — these are typical zone backgrounds
FIT_NODE_RE = re.compile(r'\\node\s*\[[^\]]*\bfit\s*=', re.IGNORECASE)

# Background-layer fills (also count as zones)
PGFONLAYER_BG_RE = re.compile(
    r'\\begin\{pgfonlayer\}\{background\}(.*?)\\end\{pgfonlayer\}',
    re.DOTALL,
)

# Plot expressions count as embedded viz directly.
PLOT_EXPR_RE = re.compile(r'\\draw\b[^;]*\bplot\b')

# Rectangle drawn with \draw (treated as a node-like element for hero detection)
DRAW_RECT_RE = re.compile(
    r'\\draw\s*\[([^\]]*)\][^;]*?'
    r'\((-?[\d.]+)\s*,\s*(-?[\d.]+)\)\s*'
    r'rectangle\s*'
    r'\((-?[\d.]+)\s*,\s*(-?[\d.]+)\)'
)

# Style definitions: `name/.style={...}` either standalone or inside \tikzset{}.
# Body capture group handles ONE level of brace nesting — needed because TikZ
# arrow styles like `-{Stealth[scale=0.9]}` contain nested `{}`.
STYLE_DEF_RE = re.compile(
    r'([A-Za-z_]\w*)\s*/\.style\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}',
    re.DOTALL,
)

# Default node geometry (matches the skill's tikz-template.tex defaults)
DEFAULT_WIDTH_CM = 2.6
DEFAULT_HEIGHT_CM = 0.9


# ─── Helpers ─────────────────────────────────────────────────────────────


def strip_comments(src: str) -> str:
    return COMMENT_RE.sub("", src)


def line_type_signature(opts: str, style_defs: dict[str, str] | None = None) -> str:
    """Reduce a \\draw option string to a comparable line-type signature.

    The signature key is `(color, dash, width)`. Two draws with the same key
    look identical to a reader; different keys mean visual variation.

    If `style_defs` is provided, `\\draw[msg]` etc. inherit the underlying
    color/dash/width from the `msg/.style={...}` definition.
    """
    if style_defs:
        opts = resolve_style_chain(opts, style_defs)

    color_match = re.search(
        r'(?:color\s*=\s*|draw\s*=\s*)([A-Za-z][\w!]*)',
        opts,
    )
    color = color_match.group(1) if color_match else "default"

    if "dashed" in opts:
        dash = "dashed"
    elif "dotted" in opts:
        dash = "dotted"
    elif "densely dashed" in opts:
        dash = "densely-dashed"
    else:
        dash = "solid"

    if "ultra thick" in opts:
        width = "ultra-thick"
    elif "very thick" in opts:
        width = "very-thick"
    elif "thick" in opts:
        width = "thick"
    elif "line width" in opts:
        m = re.search(r'line\s*width\s*=\s*([\d.]+)\s*pt', opts)
        width = f"lw-{m.group(1)}pt" if m else "lw-unknown"
    else:
        width = "default"

    return f"{color}/{dash}/{width}"


def extract_styles(src: str) -> dict[str, str]:
    """Collect all `name/.style={...}` definitions, including inside \\tikzset{}.

    Returns a flat map from style name to its option string. Used so a node
    `\\node[hero_box]` inherits `minimum width=4.6cm` declared in `hero_box/.style`.
    """
    return {name: opts for name, opts in STYLE_DEF_RE.findall(src)}


def resolve_style_chain(
    opts: str, style_defs: dict[str, str], depth: int = 0,
) -> str:
    """Expand referenced styles into the inline option string (one level deep).

    Names appearing as bare tokens in `opts` and present in `style_defs` are
    inlined. Recurses up to 3 levels to handle chains like
    `hero_box/.style={base_box, minimum width=5cm}`. Order matters: bare opts
    win over inherited (we prepend the parent so later inline opts override).
    """
    if depth > 3:
        return opts
    parts = [p.strip() for p in opts.split(",")]
    inherited: list[str] = []
    inline: list[str] = []
    for part in parts:
        token = re.split(r'\s*=\s*', part, maxsplit=1)[0].strip()
        if token in style_defs and "=" not in part:
            inherited.append(
                resolve_style_chain(style_defs[token], style_defs, depth + 1)
            )
        else:
            inline.append(part)
    # Inline first → re.search() finds them before inherited defaults, so
    # `\node[orange_node, minimum width=5.4cm]` correctly overrides
    # `orange_node/.style={base_box, ...}` whose base_box has `minimum width=2.4cm`.
    return ", ".join(filter(None, inline + inherited))


def parse_node_geometry(
    opts: str, style_defs: dict[str, str] | None = None,
) -> tuple[float, float]:
    """Return (width_cm, height_cm) for a node given its option string.

    If `style_defs` is provided, named styles in `opts` are expanded so the
    node inherits `minimum width`/`minimum height` declared in the style def.
    """
    if style_defs:
        opts = resolve_style_chain(opts, style_defs)

    w_match = MINWIDTH_RE.search(opts)
    h_match = MINHEIGHT_RE.search(opts)
    s_match = MINSIZE_RE.search(opts)

    if s_match:
        side = float(s_match.group(1))
        return side, side

    width = float(w_match.group(1)) if w_match else DEFAULT_WIDTH_CM
    height = float(h_match.group(1)) if h_match else DEFAULT_HEIGHT_CM
    return width, height


def parse_drawn_rectangles(src: str) -> list[tuple[float, float]]:
    """Return (width_cm, height_cm) for each `\\draw ... rectangle (...)` shape.

    These are commonly used as hero box outlines in templates (drawing the
    big container, with sub-nodes placed inside afterwards).
    """
    out: list[tuple[float, float]] = []
    for _opts, x1, y1, x2, y2 in DRAW_RECT_RE.findall(src):
        w = abs(float(x2) - float(x1))
        h = abs(float(y2) - float(y1))
        out.append((w, h))
    return out


def count_foreach_iterations(body: str) -> int:
    """Estimate iteration count from explicit `\\foreach … in {a, b, c}` lists.

    We split on top-level commas only (parens / braces nest). Approximate.
    """
    total = 0
    for items in FOREACH_LIST_RE.findall(body):
        depth = 0
        commas = 0
        for ch in items:
            if ch in "({[":
                depth += 1
            elif ch in ")}]":
                depth -= 1
            elif ch == "," and depth == 0:
                commas += 1
        total += commas + 1  # N commas → N+1 elements
    return total


def count_embedded_viz(body: str) -> int:
    """Embedded visualization heuristic.

    Counts:
      * \\foreach loops whose body (within balanced braces) contains \\fill or \\draw plot
      * standalone \\draw plot expressions (line charts)
    Uses a brace-balanced scan instead of regex so nested foreach
    (heatmap = outer foreach rows + inner foreach cells) is handled.
    """
    n = 0
    i = 0
    while True:
        i = body.find(r'\foreach', i)
        if i < 0:
            break
        # Find the matching `{...}` body of this foreach.
        depth = 0
        j = i
        body_start = -1
        while j < len(body):
            c = body[j]
            if c == '{':
                if depth == 0 and body_start < 0:
                    body_start = j + 1
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0 and body_start >= 0:
                    inner = body[body_start:j]
                    if r'\fill' in inner or r'\draw plot' in inner or r'plot[' in inner:
                        n += 1
                    break
            j += 1
        i = max(j, i + 1)
    n += len(PLOT_EXPR_RE.findall(body))
    return n


# ─── Core analysis ───────────────────────────────────────────────────────


def analyze(src: str) -> Metrics:
    src = strip_comments(src)
    style_defs = extract_styles(src)
    m = Metrics()

    # Nodes — resolve style chains so [server_box] sees server_box's min width
    node_opts = NODE_OPTS_RE.findall(src)
    m.node_count = len(node_opts)

    sizes_cm2: list[float] = []
    for opts in node_opts:
        w, h = parse_node_geometry(opts, style_defs)
        area = w * h
        sizes_cm2.append(area)
        if w >= DEFAULTS.min_hero_width_cm or area >= DEFAULTS.min_hero_area_cm2:
            m.hero_present = True
            m.hero_max_width_cm = max(m.hero_max_width_cm, w)
            m.hero_max_area_cm2 = max(m.hero_max_area_cm2, area)

    # Drawn rectangles also count as hero candidates (large container outlines)
    for w, h in parse_drawn_rectangles(src):
        area = w * h
        sizes_cm2.append(area)
        if w >= DEFAULTS.min_hero_width_cm or area >= DEFAULTS.min_hero_area_cm2:
            m.hero_present = True
            m.hero_max_width_cm = max(m.hero_max_width_cm, w)
            m.hero_max_area_cm2 = max(m.hero_max_area_cm2, area)

    if sizes_cm2:
        m.distinct_node_areas = len({round(a, 2) for a in sizes_cm2})
        smallest = min(sizes_cm2)
        largest = max(sizes_cm2)
        m.size_ratio = round(largest / smallest, 2) if smallest > 0 else 0.0

    # Draws and line types (resolve `\draw[msg]` → msg/.style={color=...} too)
    draw_opts = DRAW_OPTS_RE.findall(src)
    m.draw_count = len(draw_opts)
    line_types = {line_type_signature(o, style_defs) for o in draw_opts}
    m.line_type_count = len(line_types)
    m.line_type_examples = sorted(line_types)[:6]

    # Fills
    m.fill_count = len(FILL_RE.findall(src))

    # Foreach iterations (counts as visual elements)
    m.foreach_iterations = count_foreach_iterations(src)

    # Embedded viz
    m.embedded_viz_count = count_embedded_viz(src)

    # Zones
    fit_zones = len(FIT_NODE_RE.findall(src))
    bg_zones = len(PGFONLAYER_BG_RE.findall(src))
    m.zone_count = fit_zones + bg_zones

    # Total visual element count (rough but useful)
    m.element_count = (
        m.node_count + m.draw_count + m.fill_count + m.foreach_iterations
    )

    return m


def evaluate(metrics: Metrics, thresholds: DesignThresholds) -> list[Issue]:
    """Report design-ambition metrics.

    DEFAULT (advisory mode): everything is WARN, never ERROR. Simple figures
    SHOULD be simple; the linter just surfaces what's there and lets Claude
    + user decide if the complexity matches the paper's needs.

    HARD ERROR only for truly broken cases (size_ratio < 1.5 with ≥ 8 nodes
    = literally no visual hierarchy at all on a figure complex enough to need it).

    Use `--strict` to upgrade WARN → ERROR if the project really wants the
    historical "max design ambition" gates.
    """
    issues: list[Issue] = []

    def warn(metric: str, actual, threshold, msg: str) -> None:
        if actual < threshold:
            issues.append(Issue("WARN", metric, actual, threshold, msg))

    warn(
        "element_count", metrics.element_count, thresholds.min_element_count,
        f"信息密度：{metrics.element_count} 个元素 < 建议 {thresholds.min_element_count}。"
        f" 复杂论文图通常 ≥ 30 元素，但简单图（贝叶斯网络/几何/对比图）少元素是合理的。"
        f" Claude + 用户判断本图是否匹配论文复杂度。",
    )

    # Hard ERROR only when the figure is complex enough to need hierarchy AND has none.
    if metrics.node_count >= 8 and 0 < metrics.size_ratio < 1.5:
        issues.append(Issue(
            "ERROR", "size_ratio", metrics.size_ratio, 1.5,
            f"严重视觉问题：{metrics.node_count} 个节点但所有框面积比 = {metrics.size_ratio:.1f}。"
            f" 这么多元素必须有视觉层次，否则读者看不出主次。给核心模块加大尺寸。",
        ))
    else:
        warn(
            "size_ratio", metrics.size_ratio, thresholds.min_size_ratio,
            f"视觉层次：最大/最小节点面积比 = {metrics.size_ratio:.1f}。"
            f" 复杂图建议 ≥ 3× 让 hero 模块明显比辅助大。",
        )

    # Hero advisory — never ERROR. Simple figures don't need a hero.
    hero_required = (
        thresholds.min_hero_width_cm > 0 or thresholds.min_hero_area_cm2 > 0
    )
    if hero_required and not metrics.hero_present:
        issues.append(Issue(
            "WARN", "hero_present", 0, 1,
            f"未发现 hero 框（宽 ≥ {thresholds.min_hero_width_cm}cm 或面积 ≥ {thresholds.min_hero_area_cm2}cm²）。"
            f" 复杂图通常有一个主导模块；如果本图所有模块语义平等（如对比/三栏图），可忽略。",
        ))

    warn(
        "line_type_count", metrics.line_type_count, thresholds.min_line_type_count,
        f"线型：{metrics.line_type_count} 种 < 建议 {thresholds.min_line_type_count}。"
        f" 如果图里有数据流/控制流/反馈不同语义，用不同线型区分。",
    )
    warn(
        "zone_count", metrics.zone_count, thresholds.min_zone_count,
        f"分组：{metrics.zone_count} 个 zone < 建议 {thresholds.min_zone_count}。"
        f" 多阶段/多层图建议加 zone 背景；单一组件图无需 zone。",
    )
    warn(
        "embedded_viz_count", metrics.embedded_viz_count,
        thresholds.min_embedded_viz_count,
        f"嵌入可视化：{metrics.embedded_viz_count} 个 < 建议 {thresholds.min_embedded_viz_count}。"
        f" 只有当论文中有可量化信息（attention/曲线/柱状）时才嵌入；纯流程图不需要。",
    )

    return issues


# ─── CLI ─────────────────────────────────────────────────────────────────


def render_human(metrics: Metrics, issues: list[Issue]) -> str:
    out: list[str] = []
    out.append("=" * 60)
    out.append("TikZ 设计野心检查")
    out.append("=" * 60)
    out.append("")
    out.append(f"  元素总数:     {metrics.element_count}")
    out.append(f"    节点:       {metrics.node_count}")
    out.append(f"    \\draw:      {metrics.draw_count}")
    out.append(f"    \\fill:      {metrics.fill_count}")
    out.append(f"    foreach 项:  {metrics.foreach_iterations}")
    out.append(f"  尺寸多样性:    {metrics.distinct_node_areas} 种节点尺寸；最大/最小 = {metrics.size_ratio:.1f}")
    out.append(f"  Hero 框:      {'是' if metrics.hero_present else '否'}"
                f"（最宽 {metrics.hero_max_width_cm:.1f}cm，最大面积 {metrics.hero_max_area_cm2:.1f}cm²）")
    out.append(f"  线型种类:      {metrics.line_type_count}  例: {', '.join(metrics.line_type_examples[:4])}")
    out.append(f"  Zone 数:       {metrics.zone_count}")
    out.append(f"  嵌入可视化:    {metrics.embedded_viz_count}")
    out.append("")

    if not issues:
        out.append("✓ PASS — 全部设计门槛通过")
        return "\n".join(out)

    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]

    if errors:
        out.append(f"✗ {len(errors)} 个 ERROR (必须修复):")
        for i in errors:
            out.append(f"   [{i.metric}] {i.message}")
    if warns:
        out.append(f"⚠ {len(warns)} 个 WARN (建议修复):")
        for i in warns:
            out.append(f"   [{i.metric}] {i.message}")

    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TikZ design-ambition linter — structural quality gate.",
    )
    parser.add_argument("tex_file", type=Path, help="Input .tex file")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of human-readable text")
    parser.add_argument("--strict", action="store_true",
                        help="Treat WARN as ERROR (exit code 2 instead of 1)")
    parser.add_argument("--type", choices=list(TYPE_PRESETS),
                        default="rich",
                        help="Diagram-type preset (default: rich). "
                        "Use 'sequence' for time-sequence diagrams, "
                        "'simple' for small architecture sketches.")
    args = parser.parse_args()
    thresholds = TYPE_PRESETS[args.type]

    if not args.tex_file.is_file():
        print(f"FAIL: file not found: {args.tex_file}", file=sys.stderr)
        return 2

    src = args.tex_file.read_text(encoding="utf-8", errors="replace")
    metrics = analyze(src)
    issues = evaluate(metrics, thresholds)

    has_error = any(i.level == "ERROR" for i in issues)
    has_warn = any(i.level == "WARN" for i in issues)

    if args.json:
        payload = {
            "file": str(args.tex_file),
            "type": args.type,
            "status": "fail" if has_error else ("warn" if has_warn else "pass"),
            "metrics": asdict(metrics),
            "thresholds": asdict(thresholds),
            "issues": [asdict(i) for i in issues],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(metrics, issues))

    if has_error:
        return 2
    if has_warn and args.strict:
        return 2
    if has_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
