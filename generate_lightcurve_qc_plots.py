#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------
# Column mapping and utilities
# ------------------------------
DEFAULT_COL_MAP = {
    # Logical name -> candidate column names in order of preference
    "source_id": ["source_id", "object_id", "id", "oid", "ztf_id"],
    "time": ["mjd", "time", "jd", "hjd"],
    "mag": ["mag", "magnitude", "mag_aperture", "mag_psf", "magpsf", "magpsf_corr"],
    "mag_err": ["mag_err", "magerr", "mag_error", "mag_aperture_err", "mag_psf_err", "sigmapsf"],
    "flag": ["flag", "quality_flag", "dq", "flags", "catflags"],
    "astro_sep_arcsec": ["astro_sep_arcsec", "separation_arcsec", "sep_arcsec", "match_sep_arcsec"],
    # Optional band column
    "band": ["band", "filter", "fid", "ztf_filter"],
}


def resolve_columns(df: pd.DataFrame, col_map: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
    resolved = {}
    for key, candidates in col_map.items():
        found = None
        for c in candidates:
            if c in df.columns:
                found = c
                break
        resolved[key] = found
    return resolved


# ------------------------------
# Quality cuts
# ------------------------------
@dataclass
class QualityCuts:
    min_points: int = 10
    max_mag_err: float = 0.2
    allowed_flags: Optional[List[int]] = None  # If None, treat NaN or 0 as good
    max_astro_sep_arcsec: Optional[float] = 2.0


def apply_point_level_filters(df: pd.DataFrame, cols: Dict[str, Optional[str]], qc: QualityCuts) -> pd.Series:
    mask = pd.Series(True, index=df.index)

    # mag_err cut
    if cols.get("mag_err") and qc.max_mag_err is not None:
        magerr = pd.to_numeric(df[cols["mag_err"]], errors="coerce")
        mask &= magerr.notna() & (magerr <= qc.max_mag_err)

    # flag cut
    if cols.get("flag"):
        flags = pd.to_numeric(df[cols["flag"]], errors="coerce")
        if qc.allowed_flags is None:
            # Keep NaN or 0 as good by default
            mask &= (flags.isna()) | (flags == 0)
        else:
            mask &= flags.isin(qc.allowed_flags)

    # astrometric separation cut (if per-row separation exists)
    if cols.get("astro_sep_arcsec") and qc.max_astro_sep_arcsec is not None:
        sep = pd.to_numeric(df[cols["astro_sep_arcsec"]], errors="coerce")
        mask &= sep.notna() & (sep <= qc.max_astro_sep_arcsec)

    return mask


def group_and_filter_sources(df: pd.DataFrame, cols: Dict[str, Optional[str]], qc: QualityCuts) -> Tuple[pd.DataFrame, Dict[str, int]]:
    stats = {
        "total_rows": int(len(df)),
        "total_sources": int(df[cols["source_id"]].nunique() if cols.get("source_id") else 0),
        "removed_point_magerr": 0,
        "removed_point_flags": 0,
        "removed_point_astsep": 0,
        "kept_points": 0,
        "removed_sources_minpoints": 0,
        "kept_sources": 0,
    }

    # Point-level filters
    base_mask = pd.Series(True, index=df.index)
    # Track individual masks for statistics
    magerr_mask = pd.Series(True, index=df.index)
    flags_mask = pd.Series(True, index=df.index)
    astsep_mask = pd.Series(True, index=df.index)

    if cols.get("mag_err") and qc.max_mag_err is not None:
        magerr = pd.to_numeric(df[cols["mag_err"]], errors="coerce")
        magerr_mask = magerr.notna() & (magerr <= qc.max_mag_err)
        base_mask &= magerr_mask

    if cols.get("flag"):
        flags = pd.to_numeric(df[cols["flag"]], errors="coerce")
        if qc.allowed_flags is None:
            flags_mask = (flags.isna()) | (flags == 0)
        else:
            flags_mask = flags.isin(qc.allowed_flags)
        base_mask &= flags_mask

    if cols.get("astro_sep_arcsec") and qc.max_astro_sep_arcsec is not None:
        sep = pd.to_numeric(df[cols["astro_sep_arcsec"]], errors="coerce")
        astsep_mask = sep.notna() & (sep <= qc.max_astro_sep_arcsec)
        base_mask &= astsep_mask

    stats["removed_point_magerr"] = int((~magerr_mask).sum())
    stats["removed_point_flags"] = int((~flags_mask).sum())
    stats["removed_point_astsep"] = int((~astsep_mask).sum())

    df_points = df[base_mask].copy()
    stats["kept_points"] = int(len(df_points))

    # Source-level minimum points
    if not cols.get("source_id"):
        # If we cannot identify source ids, we cannot do source-level filtering
        df_sources = df_points
    else:
        counts = df_points.groupby(cols["source_id"]).size()
        keep_ids = counts[counts >= qc.min_points].index
        stats["removed_sources_minpoints"] = int((counts < qc.min_points).sum())
        df_sources = df_points[df_points[cols["source_id"]].isin(keep_ids)]
        stats["kept_sources"] = int(len(keep_ids))

    return df_sources, stats


# ------------------------------
# Plotting
# ------------------------------

def plot_lightcurve(df: pd.DataFrame, cols: Dict[str, Optional[str]], outpath: Path, source_id_val, bands: Optional[pd.Series] = None):
    time_col = cols.get("time")
    mag_col = cols.get("mag")
    err_col = cols.get("mag_err")
    flag_col = cols.get("flag")
    band_col = cols.get("band")

    if time_col is None or mag_col is None:
        return

    t = pd.to_numeric(df[time_col], errors="coerce")
    m = pd.to_numeric(df[mag_col], errors="coerce")
    yerr = pd.to_numeric(df[err_col], errors="coerce") if err_col else None
    flags = pd.to_numeric(df[flag_col], errors="coerce") if flag_col else None

    plt.figure(figsize=(8, 5))

    # Color by band if present, else single color
    if band_col and band_col in df.columns:
        bands = df[band_col].astype(str)
        uniq_bands = bands.unique()
        cmap = plt.cm.get_cmap('tab10', len(uniq_bands))
        for i, b in enumerate(uniq_bands):
            sel = bands == b
            if yerr is not None:
                plt.errorbar(t[sel], m[sel], yerr=yerr[sel], fmt='o', ms=3, lw=0.5, alpha=0.9, label=f"{b}", color=cmap(i))
            else:
                plt.plot(t[sel], m[sel], 'o', ms=3, alpha=0.9, label=f"{b}", color=cmap(i))
    else:
        if yerr is not None:
            plt.errorbar(t, m, yerr=yerr, fmt='o', ms=3, lw=0.5, alpha=0.9)
        else:
            plt.plot(t, m, 'o', ms=3, alpha=0.9)

    # Astronomy convention: brighter up means invert y-axis
    plt.gca().invert_yaxis()

    # Labels and title
    npts = len(df)
    title_parts = [f"ID={source_id_val}", f"N={npts}"]
    if err_col:
        med_err = pd.to_numeric(df[err_col], errors="coerce").median()
        title_parts.append(f"med_err={med_err:.3f}")
    med_mag = pd.to_numeric(df[mag_col], errors="coerce").median()
    title_parts.append(f"med_mag={med_mag:.3f}")

    plt.title(" | ".join(title_parts))
    plt.xlabel(time_col)
    plt.ylabel(mag_col)
    plt.grid(True, alpha=0.2)
    if band_col and band_col in df.columns:
        plt.legend(fontsize=8, loc='best')

    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


# ------------------------------
# IO utilities
# ------------------------------

def load_candidate_tables() -> List[Tuple[str, pd.DataFrame]]:
    """
    Heuristically load plausible lightcurve-like tables from the repository.
    Priority: culled_csvs/*.csv, ztf_analysis/*.csv.
    If multiple files exist, concatenate those that share required columns.
    """
    roots = [
        Path("culled_csvs"),
        Path("ztf_analysis"),
        Path("ztf_candidates"),
    ]
    loaded = []
    for r in roots:
        if not r.exists():
            continue
        for p in sorted(r.glob("*.csv")):
            try:
                df = pd.read_csv(p)
                loaded.append((str(p), df))
            except Exception:
                continue
    return loaded


# ------------------------------
# Main
# ------------------------------


def main():
    parser = argparse.ArgumentParser(description="Apply lightcurve quality cuts and generate sample QA plots.")
    parser.add_argument("--min-points", type=int, default=10, help="Minimum number of points per source after cuts.")
    parser.add_argument("--max-mag-err", type=float, default=0.2, help="Maximum per-point magnitude error to keep.")
    parser.add_argument("--allowed-flags", type=str, default=None, help="Comma-separated list of allowed flag values. If omitted, keep NaN or 0.")
    parser.add_argument("--max-astro-sep", type=float, default=2.0, help="Maximum astrometric separation in arcsec (if column exists).")
    parser.add_argument("--sample-size", type=int, default=100, help="Number of sources to plot at most.")
    parser.add_argument("--outdir", type=str, default="plotting_tool_graphs/lightcurve_qc_samples", help="Output directory for QA plots and summaries.")
    parser.add_argument("--input", type=str, default=None, help="Optional explicit CSV path to use as input.")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.allowed_flags is None or args.allowed_flags.strip() == "":
        allowed_flags = None
    else:
        allowed_flags = [int(x) for x in args.allowed_flags.split(',') if x.strip() != ""]

    qc = QualityCuts(
        min_points=args.min_points,
        max_mag_err=args.max_mag_err,
        allowed_flags=allowed_flags,
        max_astro_sep_arcsec=args.max_astro_sep,
    )

    # Load input
    inputs = []
    if args.input:
        p = Path(args.input)
        if not p.exists():
            raise FileNotFoundError(f"Input file not found: {p}")
        inputs = [(str(p), pd.read_csv(p))]
    else:
        inputs = load_candidate_tables()

    if not inputs:
        info_path = outdir / "NO_INPUTS_FOUND.txt"
        info_path.write_text(
            "No candidate CSVs found. Place a lightcurve CSV in culled_csvs/ or pass --input.\n"
        )
        print(info_path.read_text())
        return

    # Identify the first input that looks like a lightcurve table
    selected_name, selected_df = None, None
    for name, df in inputs:
        cols = resolve_columns(df, DEFAULT_COL_MAP)
        if cols.get("source_id") and cols.get("time") and cols.get("mag"):
            selected_name, selected_df = name, df
            break

    if selected_df is None:
        info_path = outdir / "NO_COMPATIBLE_INPUTS.txt"
        info_path.write_text(
            "No CSV found with at least source_id, time, mag columns (per DEFAULT_COL_MAP).\n"
        )
        print(info_path.read_text())
        return

    # Resolve columns and coerce types of key fields
    cols = resolve_columns(selected_df, DEFAULT_COL_MAP)
    sid_col = cols["source_id"]

    # Apply cuts
    filtered_df, cut_stats = group_and_filter_sources(selected_df, cols, qc)

    # Save cut summary
    cut_summary = {
        "input_file": selected_name,
        "col_map": cols,
        "quality_cuts": {
            "min_points": qc.min_points,
            "max_mag_err": qc.max_mag_err,
            "allowed_flags": qc.allowed_flags,
            "max_astro_sep_arcsec": qc.max_astro_sep_arcsec,
        },
        "stats": cut_stats,
    }
    (outdir / "cut_summary.json").write_text(json.dumps(cut_summary, indent=2))

    # Prepare per-source plotting
    if sid_col is None:
        info_path = outdir / "NO_SOURCE_ID.txt"
        info_path.write_text("Cannot plot per-source lightcurves without a source_id column.\n")
        print(info_path.read_text())
        return

    # Compute before/after N points per source histograms
    before_counts = selected_df.groupby(sid_col).size()
    after_counts = filtered_df.groupby(sid_col).size()

    # Histogram plot
    plt.figure(figsize=(8, 4))
    bins = np.linspace(0, max(before_counts.max() if len(before_counts) else 1, qc.min_points * 2), 30)
    if len(before_counts):
        plt.hist(before_counts.values, bins=bins, alpha=0.5, label="before")
    if len(after_counts):
        plt.hist(after_counts.values, bins=bins, alpha=0.5, label="after")
    plt.xlabel("N points per source")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "npoints_hist_before_after.png")
    plt.close()

    # Select up to sample_size sources to plot
    unique_ids = after_counts.sort_values(ascending=False).index.tolist()
    sample_ids = unique_ids[: args.sample_size]

    index_rows = []

    for sid in sample_ids:
        sdf = filtered_df[filtered_df[sid_col] == sid].copy()
        if len(sdf) == 0:
            continue
        # Sort by time for nicer plots
        tcol = cols.get("time")
        if tcol:
            sdf = sdf.sort_values(by=tcol)
        out_png = outdir / f"lc_{sid}.png"
        plot_lightcurve(sdf, cols, out_png, sid)

        med_mag = pd.to_numeric(sdf[cols["mag"]], errors="coerce").median()
        med_err = pd.to_numeric(sdf[cols["mag_err"]], errors="coerce").median() if cols.get("mag_err") else np.nan
        index_rows.append({
            "source_id": sid,
            "n_points": int(len(sdf)),
            "median_mag": float(med_mag) if pd.notna(med_mag) else np.nan,
            "median_mag_err": float(med_err) if pd.notna(med_err) else np.nan,
            "plot_path": str(out_png),
        })

    # Write index CSV
    index_df = pd.DataFrame(index_rows)
    index_df.to_csv(outdir / "index.csv", index=False)

    # Also emit a small README with guidance
    readme = f"""
Lightcurve QA sample outputs
============================

Input file: {selected_name}

This directory contains:
- cut_summary.json: configuration and counts before/after the quality cuts
- npoints_hist_before_after.png: distribution of points per source
- index.csv: list of plotted source_ids and their stats
- lc_*.png: per-source lightcurve plots (mag vs time) with error bars when available

Default cuts:
- min_points = {qc.min_points}
- max_mag_err = {qc.max_mag_err}
- allowed_flags = {qc.allowed_flags if qc.allowed_flags is not None else 'NaN or 0 treated as good'}
- max_astro_sep_arcsec = {qc.max_astro_sep_arcsec}

Adjust and rerun, e.g.:
    python3 generate_lightcurve_qc_plots.py --min-points 15 --max-mag-err 0.15 --max-astro-sep 2.0 --sample-size 100
"""
    (outdir / "README.txt").write_text(readme.strip() + "\n")

    print(f"Wrote QA plots for {len(index_rows)} sources to {outdir}")


if __name__ == "__main__":
    main()
