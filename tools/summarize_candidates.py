#!/usr/bin/env python3
"""
Create a small, readable summary from candidates/interesting_objects.csv.

This is intentionally heuristic. It looks for keywords inside raw_text and
produces a short markdown report to help prioritize follow-up.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


KEYWORDS = [
    ("transient", ["transient", "at "]),
    ("periodic", ["periodic"]),
    ("irregular", ["irregular"]),
    ("lpv", ["long-period variable", "lpv"]),
    ("pn", ["planetary nebula", " pn "]),
    ("yso", ["young stellar object"]),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize candidate table into markdown.")
    parser.add_argument(
        "--csv",
        type=str,
        default=str(PROJECT_ROOT / "candidates" / "interesting_objects.csv"),
        help="Input CSV path.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(PROJECT_ROOT / "candidates" / "SUMMARY.md"),
        help="Output markdown path.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_path = Path(args.out)

    rows = []
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)

    class_counts = Counter(r.get("neowise_class", "") or "Unknown" for r in rows)

    bucketed: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        raw = r.get("raw_text", "") or ""
        # Normalize case and whitespace for more robust keyword hits.
        raw_norm = " ".join(raw.lower().split())
        oid = r.get("object_id", "") or ""
        for label, keys in KEYWORDS:
            if any(k in raw_norm for k in keys):
                bucketed[label].append(oid)

    # Notable targets: anything that looks like a transient or potential contaminant.
    notable = []
    for r in rows:
        raw = r.get("raw_text", "") or ""
        raw_norm = " ".join(raw.lower().split())
        oid = r.get("object_id", "") or ""
        reasons = []
        if "transient" in raw_norm or "at " in raw_norm:
            reasons.append("transient-like label")
        if "planetary nebula" in raw_norm:
            reasons.append("possible PN contamination")
        if "long-period variable" in raw_norm:
            reasons.append("LPV candidate")
        if reasons:
            notable.append((oid, "; ".join(reasons)))

    lines = []
    lines.append("# Candidate Summary")
    lines.append("")
    try:
        rel = csv_path.relative_to(PROJECT_ROOT)
        lines.append(f"Source: `{rel}`")
    except ValueError:
        lines.append(f"Source: `{csv_path}`")
    lines.append("")
    lines.append(f"Total rows: {len(rows)}")
    lines.append("")
    lines.append("## Counts by NEOWISE class")
    lines.append("")
    for cls, n in class_counts.most_common():
        lines.append(f"- {cls}: {n}")
    lines.append("")
    lines.append("## Keyword flags (from raw_text)")
    lines.append("")
    for label, _ in KEYWORDS:
        ids = bucketed.get(label, [])
        lines.append(f"- {label}: {len(ids)}")
    lines.append("")
    lines.append("## Notable targets to sanity-check first")
    lines.append("")
    if not notable:
        lines.append("- None flagged by keyword heuristics")
    else:
        for oid, reason in notable:
            lines.append(f"- {oid}: {reason}")
    lines.append("")
    lines.append("## How to use this")
    lines.append("")
    lines.append("- Start with transient-like and contaminant-like entries to verify classification.")
    lines.append("- For each target, inspect NEOWISE W1/W2 light curves and check ZTF behavior matches the label.")
    lines.append("- Confirm counterpart association using match separation and Gaia consistency when available.")
    lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
