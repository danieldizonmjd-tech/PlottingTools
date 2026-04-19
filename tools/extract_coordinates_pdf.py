#!/usr/bin/env python3
"""
Extract a best-effort table from candidates/table_of_coordinates.pdf.

The PDF is a human-formatted table that wraps cells across lines.
This script extracts per-object "blocks" and pulls out the fields that are
reliably machine-readable (object id, RA, Dec, NEOWISE class).

It also keeps the full raw block text so no information is lost.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]


CLASS_TOKENS = {"ClassI", "ClassII", "ClassIII", "FS", "Linear", "uncertain"}


ID_RE = re.compile(r"^\d{3,}$")
FLOAT_RE = re.compile(r"^[+-]?\d+\.\d+$")


@dataclass
class Row:
    object_id: str
    ra_deg: str
    dec_deg: str
    neowise_class: str
    raw_text: str


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        chunks.append(t)
    return "\n".join(chunks)


def split_blocks(text: str) -> list[str]:
    """
    Split into blocks that start with an integer object id.
    We keep the header lines out by requiring >=3 digits.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    blocks: list[list[str]] = []
    cur: list[str] = []

    def flush():
        nonlocal cur
        if cur:
            blocks.append(cur)
            cur = []

    for ln in lines:
        first = ln.split()[0]
        if ID_RE.match(first):
            flush()
            cur.append(ln)
        else:
            if cur:
                cur.append(ln)
            # else: ignore pre-header noise
    flush()

    return [" ".join(b) for b in blocks]


def parse_block(block: str) -> Row | None:
    """
    Best-effort parse.

    Expected early tokens:
    - object_id (int)
    - RA (float)
    - Dec (float)
    Then somewhere soon: class token.
    """
    toks = block.split()
    if len(toks) < 3:
        return None
    if not ID_RE.match(toks[0]):
        return None

    object_id = toks[0]

    # Find first RA/Dec float pair after object id.
    ra = ""
    dec = ""
    for i in range(1, len(toks) - 1):
        if FLOAT_RE.match(toks[i]) and FLOAT_RE.match(toks[i + 1]):
            ra = toks[i]
            dec = toks[i + 1]
            break
    if not ra or not dec:
        # Some blocks may have formatting issues; keep raw.
        ra = ""
        dec = ""

    neowise_class = ""
    for t in toks:
        if t in CLASS_TOKENS:
            neowise_class = t
            break

    return Row(
        object_id=object_id,
        ra_deg=ra,
        dec_deg=dec,
        neowise_class=neowise_class,
        raw_text=block,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract coordinates table PDF into a CSV.")
    parser.add_argument(
        "--pdf",
        type=str,
        default=str(PROJECT_ROOT / "candidates" / "table_of_coordinates.pdf"),
        help="Input PDF path.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(PROJECT_ROOT / "candidates" / "interesting_objects.csv"),
        help="Output CSV path.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    text = extract_text(pdf_path)
    blocks = split_blocks(text)
    rows: list[Row] = []
    for b in blocks:
        r = parse_block(b)
        if r:
            rows.append(r)

    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["object_id", "ra_deg", "dec_deg", "neowise_class", "raw_text"])
        for r in rows:
            w.writerow([r.object_id, r.ra_deg, r.dec_deg, r.neowise_class, r.raw_text])

    print(f"Wrote {len(rows)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

