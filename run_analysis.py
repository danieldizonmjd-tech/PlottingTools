#!/usr/bin/env python3
"""
One-command entry point for the core analysis.

This runs the two scripts that produce the main figures used in the repo README:
- generate_improved_visualizations.py
- generate_dispersion_vs_median_plots.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the core YSO plotting analysis.")
    parser.add_argument(
        "--skip-dispersion",
        action="store_true",
        help="Skip dispersion vs magnitude diagnostic plots.",
    )
    args = parser.parse_args()

    py = sys.executable or "python3"

    run([py, "generate_improved_visualizations.py"])
    if not args.skip_dispersion:
        run([py, "generate_dispersion_vs_median_plots.py"])

    print("\nOutputs are written to: plotting_tool_graphs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

