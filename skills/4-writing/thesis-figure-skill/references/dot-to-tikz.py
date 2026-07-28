#!/usr/bin/env python3
"""figure-spec.json → graphviz dot → TikZ.

B path of the skill: structural diagrams (architecture, pipeline, DAG,
hierarchy) where Claude has no business picking (x, y) coordinates.
Layout is computed by Graphviz; we generate a TikZ file using academic
styles and the computed positions.

Usage:
    python3 dot-to-tikz.py spec.json [-o figure.tex]

Requires:
    - graphviz on PATH (`brew install graphviz` / `apt install graphviz`)
    - figure-spec.schema.md for the input format

Output:
    A complete xelatex-compileable .tex file. Run xelatex + pdftoppm as usual.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ─── Constants ───────────────────────────────────────────────────────────

# Graphviz uses 72 points per inch; TikZ default unit is cm. 1 inch = 2.54 cm.
GV_POINTS_PER_INCH = 72.0
CM_PER_INCH = 2.54
GV_POINT_TO_CM = CM_PER_INCH / GV_POINTS_PER_INCH  # ~0.0353

NODE_SIZE_PRESETS = {
    "small":  (1.4, 0.6),
    "normal": (2.8, 0.9),
    "hero":   (5.6, 2.4),
}

EDGE_STYLE_TIKZ = {
    "main":     "-{Stealth[scale=1.1]}, line width=1.3pt, color=acaOrangeLine, shorten >=6pt, shorten <=1pt",
    "control":  "-{Stealth[scale=0.9]}, thick, color=black!70, shorten >=6pt, shorten <=1pt",
    "feedback": "-{Stealth[scale=0.8]}, dashed, thick, color=acaRedLine!85, line width=0.9pt, shorten >=6pt, shorten <=1pt",
    "contrast": "-{Stealth[scale=0.8]}, dashed, thick, color=acaPurpleLine!85, line width=0.9pt, shorten >=6pt, shorten <=1pt",
}

COLOR_NAME_TO_STYLE = {
    "blue":   "blue_node",
    "green":  "green_node",
    "orange": "orange_node",
    "purple": "purple_node",
    "red":    "red_node",
    "grey":   "grey_node",
    "gold":   "gold_node",
    "teal":   "teal_node",
    "cyan":   "cyan_node",
    "pink":   "pink_node",
    "yellow": "yellow_node",
    "lime":   "lime_node",
}

ZONE_BG_BY_COLOR = {
    "blue":   "zoneBlueBg",
    "green":  "zoneGreenBg",
    "orange": "zoneOrangeBg",
    "purple": "zonePurpleBg",
    "red":    "zoneRedBg",
    "yellow": "zoneYellowBg",
}


# ─── Spec validation ─────────────────────────────────────────────────────


@dataclass
class SpecError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def validate_spec(spec: dict[str, Any]) -> None:
    if "nodes" not in spec or not isinstance(spec["nodes"], list):
        raise SpecError("spec.nodes is required and must be a list")
    node_ids: set[str] = set()
    for n in spec["nodes"]:
        nid = n.get("id")
        if not nid or not isinstance(nid, str):
            raise SpecError(f"node missing id: {n}")
        if nid in node_ids:
            raise SpecError(f"duplicate node id: {nid}")
        node_ids.add(nid)
    for e in spec.get("edges", []):
        if e.get("from") not in node_ids:
            raise SpecError(f"edge references unknown node: {e.get('from')}")
        if e.get("to") not in node_ids:
            raise SpecError(f"edge references unknown node: {e.get('to')}")
    for z in spec.get("zones", []):
        for m in z.get("members", []):
            if m not in node_ids:
                raise SpecError(f"zone {z.get('id')} references unknown node: {m}")


# ─── Graphviz layout ─────────────────────────────────────────────────────


def build_dot_source(spec: dict[str, Any]) -> str:
    layout = spec.get("layout", {})
    rankdir = layout.get("rankdir", "LR")
    nodesep = layout.get("nodesep", 0.6)
    ranksep = layout.get("ranksep", 1.0)

    lines: list[str] = [
        "digraph G {",
        f"  rankdir={rankdir};",
        f"  nodesep={nodesep};",
        f"  ranksep={ranksep};",
        "  node [shape=box, fontname=\"Helvetica\"];",
        "  edge [fontname=\"Helvetica\"];",
        "  compound=true;",
    ]

    # Tell graphviz each node's intended size so layout reserves room.
    for n in spec["nodes"]:
        size = NODE_SIZE_PRESETS.get(n.get("size", "normal"),
                                     NODE_SIZE_PRESETS["normal"])
        w_in, h_in = size[0] / CM_PER_INCH, size[1] / CM_PER_INCH
        # `label="\\N"` so graphviz uses node id; we replace text in TikZ later
        lines.append(
            f'  {n["id"]} [width={w_in:.2f}, height={h_in:.2f}, '
            f'fixedsize=true, label="\\N"];'
        )

    # Clusters for zones
    for i, z in enumerate(spec.get("zones", [])):
        lines.append(f"  subgraph cluster_{i} {{")
        lines.append(f'    label="{z.get("label", z["id"])}";')
        lines.append("    style=filled;")
        lines.append(f"    color=lightgrey;")
        for m in z.get("members", []):
            lines.append(f"    {m};")
        lines.append("  }")

    # Edges
    for e in spec.get("edges", []):
        lines.append(f'  {e["from"]} -> {e["to"]};')

    lines.append("}")
    return "\n".join(lines)


def run_graphviz(dot_source: str, engine: str = "dot") -> str:
    """Run graphviz on dot source and return xdot output (positions filled in)."""
    if not shutil.which(engine):
        raise SpecError(
            f"`{engine}` not found on PATH. Install graphviz: "
            f"brew install graphviz / apt install graphviz"
        )
    result = subprocess.run(
        [engine, "-Txdot"],
        input=dot_source,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SpecError(f"graphviz failed:\n{result.stderr}")
    return result.stdout


# ─── xdot parsing ────────────────────────────────────────────────────────


NODE_POS_RE = re.compile(
    r'^\s*([A-Za-z_]\w*)\s*\['
    r'(?=[^]]*?\bpos\s*=\s*"(-?[\d.]+)\s*,\s*(-?[\d.]+)")'
    r'(?=[^]]*?\bwidth\s*=\s*"?([\d.]+))'
    r'(?=[^]]*?\bheight\s*=\s*"?([\d.]+))',
    re.MULTILINE,
)
BB_RE = re.compile(r'\bbb\s*=\s*"([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)"')


@dataclass(frozen=True)
class NodePos:
    name: str
    cx_cm: float        # center x in cm (TikZ coordinates)
    cy_cm: float        # center y in cm (TikZ coordinates, y-flipped)
    w_cm: float
    h_cm: float


def parse_xdot(xdot: str) -> tuple[list[NodePos], tuple[float, float]]:
    """Return (positioned_nodes, (canvas_w_cm, canvas_h_cm))."""
    bb = BB_RE.search(xdot)
    if not bb:
        raise SpecError("could not find canvas bb in xdot output")
    _, _, x_max, y_max = (float(v) for v in bb.groups())
    canvas_w_cm = x_max * GV_POINT_TO_CM
    canvas_h_cm = y_max * GV_POINT_TO_CM

    nodes: list[NodePos] = []
    for m in NODE_POS_RE.finditer(xdot):
        name, gx, gy, gw, gh = m.groups()
        cx_cm = float(gx) * GV_POINT_TO_CM
        # Flip y: graphviz origin is bottom-left of the bb in xdot's
        # internal coords, but bb is given as (0,0,xmax,ymax) so y is
        # already bottom-up positive. Just translate.
        cy_cm = float(gy) * GV_POINT_TO_CM
        w_cm = float(gw) * CM_PER_INCH      # graphviz width attr is in inches
        h_cm = float(gh) * CM_PER_INCH
        nodes.append(NodePos(name, cx_cm, cy_cm, w_cm, h_cm))
    return nodes, (canvas_w_cm, canvas_h_cm)


# ─── TikZ emission ───────────────────────────────────────────────────────


PREAMBLE = r"""\documentclass[tikz,border=20pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath, amssymb}
\usepackage[fontset=none]{ctex}
\setCJKmainfont{PingFang SC}
\setCJKsansfont{PingFang SC}
\usetikzlibrary{shapes, arrows.meta, positioning, fit, backgrounds, calc, shadows}

\definecolor{acaBlueLine}{HTML}{6080B0}      \definecolor{acaBlueFill}{HTML}{DBEAFE}
\definecolor{acaGreenLine}{HTML}{30A060}     \definecolor{acaGreenFill}{HTML}{A0D0A0}
\definecolor{acaOrangeLine}{HTML}{D06020}    \definecolor{acaOrangeFill}{HTML}{FFE6CC}
\definecolor{acaPurpleLine}{HTML}{6020D0}    \definecolor{acaPurpleFill}{HTML}{E1D5E7}
\definecolor{acaRedLine}{HTML}{B05050}       \definecolor{acaRedFill}{HTML}{F8CECC}
\definecolor{acaGreyLine}{HTML}{666666}      \definecolor{acaGreyFill}{HTML}{F5F5F5}
\definecolor{acaGoldLine}{HTML}{D09000}      \definecolor{acaGoldFill}{HTML}{F8F8E0}
\definecolor{acaTealLine}{HTML}{009060}      \definecolor{acaTealFill}{HTML}{D1FAE5}
\definecolor{acaCyanLine}{HTML}{00B0D0}      \definecolor{acaCyanFill}{HTML}{E0F7FA}
\definecolor{acaPinkLine}{HTML}{D06090}      \definecolor{acaPinkFill}{HTML}{FCE4EC}
\definecolor{acaYellowLine}{HTML}{E0C060}    \definecolor{acaYellowFill}{HTML}{FFF8E1}
\definecolor{acaLimeLine}{HTML}{80B060}      \definecolor{acaLimeFill}{HTML}{E8F5E9}
\definecolor{zoneBlueBg}{HTML}{E0E8F8}
\definecolor{zoneGreenBg}{HTML}{E0F0E0}
\definecolor{zoneOrangeBg}{HTML}{FCEFE0}
\definecolor{zonePurpleBg}{HTML}{F0E8F8}
\definecolor{zoneRedBg}{HTML}{F8E0E0}
\definecolor{zoneYellowBg}{HTML}{F8F0C0}

\pgfdeclarelayer{background}
\pgfsetlayers{background,main}

\begin{document}
\begin{tikzpicture}[
    every node/.style={font=\footnotesize},
    base_box/.style={rectangle, rounded corners=3pt, align=center,
        inner sep=6pt, drop shadow={opacity=0.15}, thick},
    blue_node/.style={base_box, fill=acaBlueFill, draw=acaBlueLine},
    green_node/.style={base_box, fill=acaGreenFill, draw=acaGreenLine},
    orange_node/.style={base_box, fill=acaOrangeFill, draw=acaOrangeLine},
    purple_node/.style={base_box, fill=acaPurpleFill, draw=acaPurpleLine},
    red_node/.style={base_box, fill=acaRedFill, draw=acaRedLine, font=\footnotesize\bfseries},
    grey_node/.style={base_box, fill=acaGreyFill, draw=acaGreyLine},
    gold_node/.style={base_box, fill=acaGoldFill, draw=acaGoldLine},
    teal_node/.style={base_box, fill=acaTealFill, draw=acaTealLine},
    cyan_node/.style={base_box, fill=acaCyanFill, draw=acaCyanLine},
    pink_node/.style={base_box, fill=acaPinkFill, draw=acaPinkLine},
    yellow_node/.style={base_box, fill=acaYellowFill, draw=acaYellowLine},
    lime_node/.style={base_box, fill=acaLimeFill, draw=acaLimeLine},
]
"""


POSTAMBLE = r"""\end{tikzpicture}
\end{document}
"""


def emit_node(node_spec: dict[str, Any], pos: NodePos) -> str:
    color = node_spec.get("color", "blue")
    style = COLOR_NAME_TO_STYLE.get(color, "blue_node")
    label = node_spec.get("label", node_spec["id"])
    size = NODE_SIZE_PRESETS.get(node_spec.get("size", "normal"),
                                  NODE_SIZE_PRESETS["normal"])
    w, h = size
    font = r", font=\small\bfseries" if node_spec.get("size") == "hero" else ""
    return (
        f"\\node[{style}, minimum width={w:.2f}cm, minimum height={h:.2f}cm{font}]"
        f' ({node_spec["id"]}) at ({pos.cx_cm:.2f}, {pos.cy_cm:.2f}) {{{label}}};'
    )


def emit_edge(edge_spec: dict[str, Any]) -> str:
    style = EDGE_STYLE_TIKZ.get(edge_spec.get("style", "control"),
                                 EDGE_STYLE_TIKZ["control"])
    label = edge_spec.get("label")
    label_part = f' node[font=\\scriptsize, above, sloped] {{{label}}}' if label else ""
    return f'\\draw[{style}] ({edge_spec["from"]}) --{label_part} ({edge_spec["to"]});'


def emit_zone(zone_spec: dict[str, Any], idx: int) -> str:
    bg = ZONE_BG_BY_COLOR.get(zone_spec.get("color", "blue"), "zoneBlueBg")
    members = " ".join(f"({m})" for m in zone_spec["members"])
    label = zone_spec.get("label", "")
    label_part = (
        f"\n\\node[font=\\small\\bfseries, anchor=south, fill=white, inner sep=3pt, "
        f"rounded corners=2pt, draw=black!30] at ([yshift=0.15cm]zone{idx}.north) {{{label}}};"
        if label else ""
    )
    return (
        f"\\begin{{pgfonlayer}}{{background}}\n"
        f"  \\node[fit={members}, inner sep=12pt, fill={bg}, rounded corners=8pt] (zone{idx}) {{}};\n"
        f"\\end{{pgfonlayer}}{label_part}"
    )


def emit_tikz(spec: dict[str, Any], positions: dict[str, NodePos]) -> str:
    parts: list[str] = [PREAMBLE]
    parts.append("% ===== Nodes (positions from graphviz dot) =====")
    for n in spec["nodes"]:
        pos = positions.get(n["id"])
        if not pos:
            raise SpecError(f"node {n['id']} not positioned by graphviz")
        parts.append(emit_node(n, pos))

    if spec.get("zones"):
        parts.append("\n% ===== Zones (background layer) =====")
        for i, z in enumerate(spec["zones"]):
            parts.append(emit_zone(z, i))

    parts.append("\n% ===== Edges =====")
    for e in spec.get("edges", []):
        parts.append(emit_edge(e))

    if spec.get("title"):
        parts.append(f"\n% ===== Title =====")
        parts.append(f"% Title \"{spec['title']}\" — uncomment to render:")
        parts.append(f"% \\node[font=\\large\\bfseries, anchor=south] at (current bounding box.north) {{{spec['title']}}};")

    parts.append(POSTAMBLE)
    return "\n".join(parts)


# ─── CLI ─────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser(
        description="figure-spec.json → graphviz dot → TikZ.",
    )
    p.add_argument("spec_file", type=Path, help="Input figure-spec.json")
    p.add_argument("-o", "--output", type=Path,
                   help="Output .tex (default: alongside spec)")
    p.add_argument("--dump-dot", action="store_true",
                   help="Also print the generated dot source to stderr")
    args = p.parse_args()

    try:
        spec = json.loads(args.spec_file.read_text(encoding="utf-8"))
        validate_spec(spec)
    except (json.JSONDecodeError, SpecError) as ex:
        print(f"FAIL (spec): {ex}", file=sys.stderr)
        return 2

    engine = spec.get("layout", {}).get("engine", "dot")
    try:
        dot_src = build_dot_source(spec)
        if args.dump_dot:
            print(dot_src, file=sys.stderr)
        xdot = run_graphviz(dot_src, engine)
    except SpecError as ex:
        print(f"FAIL (layout): {ex}", file=sys.stderr)
        return 2

    nodes, _canvas = parse_xdot(xdot)
    positions = {n.name: n for n in nodes}
    tex = emit_tikz(spec, positions)

    # Drop ALL extensions so `compiler.spec.json` → `compiler.tex` (not `compiler.spec.tex`).
    default_out = args.spec_file.with_name(
        args.spec_file.name.split(".", 1)[0] + ".tex"
    )
    out = args.output or default_out
    out.write_text(tex, encoding="utf-8")
    print(f"✓ wrote {out} ({len(spec.get('nodes', []))} nodes, "
          f"{len(spec.get('edges', []))} edges, "
          f"{len(spec.get('zones', []))} zones)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
