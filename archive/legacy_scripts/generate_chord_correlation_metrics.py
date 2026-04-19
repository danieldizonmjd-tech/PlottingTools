#!/usr/bin/env python3
"""
Generate correlation summaries for variability metrics.
Replaces the chord diagram with a readable heatmap and ranked correlations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'paper_data_files'
PLOTS_DIR = PROJECT_ROOT / 'plotting_tool_graphs'
PLOTS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))
from yso_utils import parse_mrt_file, categorize_variability, compute_correlation_matrix

# QC parameters
MIN_POINTS = 10


def apply_qc_paper_b(df: pd.DataFrame, min_points: int = MIN_POINTS) -> pd.DataFrame:
    keep = df.copy()
    if 'Number' in keep.columns:
        keep = keep[keep['Number'] >= min_points]
    numeric_cols = ['W2magMean', 'sig_W2Flux', 'delW2mag', 'Period', 'slope', 'r_value', 'FLP_LSP_BOOT']
    present = [c for c in numeric_cols if c in keep.columns]
    if present:
        keep = keep.replace([np.inf, -np.inf], np.nan)
        keep = keep.dropna(subset=present)
    return keep


def main():
    print("Loading YSO data...")
    paper_b_file = str(DATA_DIR / 'illuminating_youth_mid_ir_variability_color_evolution_mrt.txt')
    df_b = parse_mrt_file(paper_b_file)
    print(f"Loaded {len(df_b)} sources (raw)\n")

    df_b = apply_qc_paper_b(df_b, min_points=MIN_POINTS)
    print(f"Kept {len(df_b)} sources after QC (Number >= {MIN_POINTS} and finite metrics)\n")

    df_b['Variability'] = categorize_variability(df_b, 'delW2mag')
    
    print("Computing standardized correlation matrix...")
    numeric_cols = [
        'W2magMean', 'W2magMed', 'sig_W2Flux', 'delW2mag', 'Period',
        'slope', 'r_value', 'FLP_LSP_BOOT', 'slope_color', 'pearson_color'
    ]
    numeric_cols = [c for c in numeric_cols if c in df_b.columns]
    corr_matrix = compute_correlation_matrix(df_b, numeric_cols, standardize=True)
    
    print("\nCorrelation Matrix (Standardized):")
    print(corr_matrix.round(3))
    
    print("\n" + "="*70)
    print("GENERATING HEATMAP + RANKED CORRELATIONS")
    print("="*70)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(f'Correlation Matrix: Variability Metrics\n(Standardized, QC: N>={MIN_POINTS}, kept={len(df_b)})',
                 fontsize=14, fontweight='bold', pad=20)
    heatmap_file = str(PLOTS_DIR / 'correlation_heatmap_variability_metrics.png')
    plt.tight_layout()
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Heatmap saved: {heatmap_file}")

    # Ranked correlations (top 10 by |r|)
    corr_abs = corr_matrix.abs()
    pairs = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j], corr_matrix.iloc[i, j], corr_abs.iloc[i, j]))
    pairs.sort(key=lambda x: x[3], reverse=True)
    top_pairs = pairs[:10]

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [f"{a} ↔ {b}" for a, b, _, _ in top_pairs]
    values = [v for _, _, v, _ in top_pairs]
    sns.barplot(x=values, y=labels, ax=ax, palette='viridis')
    ax.set_title('Top 10 Correlations (|r|)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Pearson r')
    ax.set_ylabel('')
    ranked_file = str(PLOTS_DIR / 'correlation_metrics_top10.png')
    plt.tight_layout()
    plt.savefig(ranked_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Ranked correlations saved: {ranked_file}")


if __name__ == "__main__":
    main()
