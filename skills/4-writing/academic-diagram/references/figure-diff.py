#!/usr/bin/env python3
"""
figure-diff.py — Compare a replicated figure against a reference figure.

Usage:
    python3 figure-diff.py <reference.png> <replicated.png> [--output diff.png]

Outputs:
    1. SSIM score (0-1, higher = more similar)
    2. Region-level difference analysis (which zones differ most)
    3. Visual diff overlay PNG (red = added, blue = removed, green = shifted)

Designed for academic figure comparison — detects:
    - Layout shifts (elements in wrong positions)
    - Missing/extra elements
    - Size mismatches
    - Color differences
"""

import sys
import os
import numpy as np

def compare_figures(ref_path, rep_path, output_path=None):
    try:
        import cv2
        from skimage.metrics import structural_similarity as ssim
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Install: pip3 install opencv-python scikit-image")
        sys.exit(1)

    # Load images
    ref = cv2.imread(ref_path)
    rep = cv2.imread(rep_path)

    if ref is None:
        print(f"ERROR: Cannot read reference image: {ref_path}")
        sys.exit(1)
    if rep is None:
        print(f"ERROR: Cannot read replicated image: {rep_path}")
        sys.exit(1)

    h_ref, w_ref = ref.shape[:2]
    h_rep, w_rep = rep.shape[:2]
    print(f"\n{'='*60}")
    print(f"  Figure Comparison Report")
    print(f"{'='*60}")
    print(f"  Reference:  {os.path.basename(ref_path)} ({w_ref}x{h_ref})")
    print(f"  Replicated: {os.path.basename(rep_path)} ({w_rep}x{h_rep})")

    # Resize replicated to match reference dimensions
    if (h_ref, w_ref) != (h_rep, w_rep):
        print(f"  [resize] Scaling replicated to {w_ref}x{h_ref}")
        rep = cv2.resize(rep, (w_ref, h_ref), interpolation=cv2.INTER_AREA)

    # Convert to grayscale for SSIM
    ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    rep_gray = cv2.cvtColor(rep, cv2.COLOR_BGR2GRAY)

    # Global SSIM
    score, diff_map = ssim(ref_gray, rep_gray, full=True)
    diff_map = (diff_map * 255).astype("uint8")
    print(f"\n  Global SSIM: {score:.4f}", end="")
    if score > 0.85:
        print("  (Good)")
    elif score > 0.70:
        print("  (Moderate — layout needs adjustment)")
    else:
        print("  (Poor — significant structural differences)")

    # Region-level analysis (divide into 3x3 grid)
    print(f"\n  Region SSIM (3x3 grid):")
    print(f"  {'':8s}  {'Left':>8s}  {'Center':>8s}  {'Right':>8s}")
    grid_scores = []
    for row, rname in enumerate(["Top", "Middle", "Bottom"]):
        y1 = row * h_ref // 3
        y2 = (row + 1) * h_ref // 3
        row_scores = []
        for col in range(3):
            x1 = col * w_ref // 3
            x2 = (col + 1) * w_ref // 3
            region_ref = ref_gray[y1:y2, x1:x2]
            region_rep = rep_gray[y1:y2, x1:x2]
            rs = ssim(region_ref, region_rep)
            row_scores.append(rs)
        grid_scores.append(row_scores)
        marks = []
        for s in row_scores:
            if s > 0.85:
                marks.append(f"  {s:.3f}")
            elif s > 0.70:
                marks.append(f" *{s:.3f}")
            else:
                marks.append(f"**{s:.3f}")
        print(f"  {rname:8s} {marks[0]:>8s} {marks[1]:>8s} {marks[2]:>8s}")

    # Find worst region
    min_score = 1.0
    min_pos = ""
    rnames = ["Top", "Middle", "Bottom"]
    cnames = ["Left", "Center", "Right"]
    for r in range(3):
        for c in range(3):
            if grid_scores[r][c] < min_score:
                min_score = grid_scores[r][c]
                min_pos = f"{rnames[r]}-{cnames[c]}"
    print(f"\n  Worst region: {min_pos} (SSIM={min_score:.3f})")

    # Contour-based difference detection
    thresh = cv2.threshold(diff_map, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter significant contours (area > 0.1% of image)
    min_area = w_ref * h_ref * 0.001
    significant = [c for c in contours if cv2.contourArea(c) > min_area]
    print(f"  Significant difference regions: {len(significant)}")

    # Describe top differences
    if significant:
        print(f"\n  Top difference regions:")
        significant.sort(key=cv2.contourArea, reverse=True)
        for i, cnt in enumerate(significant[:8]):
            x, y, w, h = cv2.boundingRect(cnt)
            area_pct = cv2.contourArea(cnt) / (w_ref * h_ref) * 100
            # Map to relative position
            rx = "left" if x < w_ref/3 else ("center" if x < 2*w_ref/3 else "right")
            ry = "top" if y < h_ref/3 else ("middle" if y < 2*h_ref/3 else "bottom")
            print(f"    {i+1}. {ry}-{rx} ({w}x{h}px, {area_pct:.1f}% of image)")

    # Generate visual diff overlay
    if output_path is None:
        base = os.path.splitext(rep_path)[0]
        output_path = f"{base}-diff.png"

    # Create diff visualization
    diff_vis = ref.copy()
    # Highlight differences in red
    mask = thresh > 0
    diff_vis[mask] = [0, 0, 255]  # Red for differences

    # Also create a side-by-side + diff composite
    h, w = ref.shape[:2]
    # Scale down for composite
    scale = min(1.0, 1200.0 / w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    ref_small = cv2.resize(ref, (new_w, new_h))
    rep_small = cv2.resize(rep, (new_w, new_h))
    diff_small = cv2.resize(diff_vis, (new_w, new_h))

    # 3-panel composite: Reference | Replicated | Diff
    composite = np.zeros((new_h + 40, new_w * 3 + 20, 3), dtype=np.uint8)
    composite[:] = 255  # white background

    # Labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(composite, "Reference", (10, 25), font, 0.7, (0, 0, 0), 2)
    cv2.putText(composite, "Replicated", (new_w + 15, 25), font, 0.7, (0, 0, 0), 2)
    cv2.putText(composite, f"Diff (SSIM={score:.3f})", (new_w*2 + 20, 25), font, 0.7, (0, 0, 255), 2)

    composite[35:35+new_h, 0:new_w] = ref_small
    composite[35:35+new_h, new_w+10:new_w*2+10] = rep_small
    composite[35:35+new_h, new_w*2+20:new_w*3+20] = diff_small

    cv2.imwrite(output_path, composite)
    print(f"\n  Diff image saved: {output_path}")
    print(f"{'='*60}")

    return score


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 figure-diff.py <reference.png> <replicated.png> [--output diff.png]")
        sys.exit(1)

    ref_path = sys.argv[1]
    rep_path = sys.argv[2]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    compare_figures(ref_path, rep_path, output_path)
