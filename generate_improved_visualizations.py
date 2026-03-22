#!/usr/bin/env python3
"""
Improved YSO Visualizations with Statistical Rigor
Addresses: Categorical correlation metrics, significance tests, class imbalance warnings
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

import sys

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'paper_data_files'
PLOTS_DIR = PROJECT_ROOT / 'plotting_tool_graphs'
PLOTS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))
from yso_utils import (
    parse_mrt_file, compute_correlation_matrix, categorize_variability
)

# QC parameters (defaults). Adjust as needed or wire to argparse if desired.
MIN_POINTS = 10
MAX_MAG_ERR = 0.2  # if an error proxy exists; Paper B lacks per-point errors, so we use Number>=MIN_POINTS
ALLOWED_FLAGS = None  # placeholder: Paper B tables don't expose per-point flags
MAX_ASTRO_SEP = 2.0   # placeholder: not available in Paper B tables


def apply_qc_paper_b(df: pd.DataFrame, min_points: int = MIN_POINTS) -> pd.DataFrame:
    """
    Apply minimal QC to Paper B-style summary table:
    - Require at least `min_points` measurements (uses 'Number' column)
    - Drop rows with NaNs in key numeric fields used downstream
    """
    keep = df.copy()
    if 'Number' in keep.columns:
        keep = keep[keep['Number'] >= min_points]
    # Ensure core numeric columns used later exist and are finite
    numeric_cols = ['W2magMean', 'sig_W2Flux', 'delW2mag', 'Period', 'slope', 'r_value', 'FLP_LSP_BOOT']
    present = [c for c in numeric_cols if c in keep.columns]
    if present:
        keep = keep.replace([np.inf, -np.inf], np.nan)
        keep = keep.dropna(subset=present)
    return keep


def cramers_v(x, y):
    """Calculate Cramér's V statistic for categorical association strength"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


def chi2_test(x, y):
    """Perform chi-squared test of independence"""
    confusion_matrix = pd.crosstab(x, y)
    chi2, p_value, dof, _ = chi2_contingency(confusion_matrix)
    return chi2, p_value, dof


def create_annotated_heatmap(matrix, title, filename, add_counts=None):
    """Create correlation heatmap with annotations"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def flag_rare_categories(df):
    """Identify and report rare categories"""
    threshold = 30
    rare_categories = {}
    
    for col in ['YSO_CLASS', 'LCType']:
        counts = df[col].value_counts()
        rare = counts[counts < threshold]
        if len(rare) > 0:
            rare_categories[col] = rare.to_dict()
    
    return rare_categories


def check_class_imbalance(df):
    """Check for severe class imbalance"""
    imbalance_report = {}
    
    for col in ['YSO_CLASS', 'LCType', 'Variability']:
        counts = df[col].value_counts()
        max_count = counts.max()
        min_count = counts.min()
        ratio = max_count / min_count
        max_pct = 100 * max_count / len(df)
        
        imbalance_report[col] = {
            'max_category': counts.idxmax(),
            'max_count': max_count,
            'max_pct': max_pct,
            'min_count': min_count,
            'ratio': ratio
        }
    
    return imbalance_report


def normalize_contingency(table: pd.DataFrame, axis: int = 1) -> pd.DataFrame:
    """Normalize contingency table by row (axis=1) or column (axis=0)."""
    if axis == 1:
        denom = table.sum(axis=1).replace(0, np.nan)
        return table.div(denom, axis=0)
    denom = table.sum(axis=0).replace(0, np.nan)
    return table.div(denom, axis=1)


def pearson_residuals(table: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson residuals for a contingency table."""
    chi2, p, dof, expected = chi2_contingency(table, correction=False)
    expected = pd.DataFrame(expected, index=table.index, columns=table.columns)
    residuals = (table - expected) / np.sqrt(expected)
    return residuals


def classify_irregular_subtype(row, slope_thresh=0.1, p_thresh=0.05):
    """Sub-classify Irregular light curves using color slope physics."""
    if row.get('LCType') != 'Irregular':
        return 'Non-Irregular'
    slope_color = row.get('slope_color')
    pvalue_color = row.get('pvalue_color')
    if pd.isna(slope_color) or pd.isna(pvalue_color):
        return 'Irregular: No color slope'
    if pvalue_color >= p_thresh or abs(slope_color) < slope_thresh:
        return 'Irregular: Stochastic/Low-signal'
    if slope_color > 0:
        return 'Irregular: Fader (redder when fainter)'
    return 'Irregular: Accretor (bluer when brighter)'


def main():
    print("Loading YSO data...")
    paper_b_file = str(DATA_DIR / 'apjsadc397t2_mrt.txt')
    df_b = parse_mrt_file(paper_b_file)
    print(f"Loaded {len(df_b)} sources (raw)\n")

    # Apply QC for Paper B summary table
    df_b = apply_qc_paper_b(df_b, min_points=MIN_POINTS)
    print(f"Kept {len(df_b)} sources after QC (Number >= {MIN_POINTS} and finite metrics)\n")

    df_b['Variability'] = categorize_variability(df_b, 'delW2mag')
    
    # ==================== DATA QUALITY REPORT ====================
    print("="*70)
    print("DATA QUALITY & STATISTICAL VALIDATION")
    print("="*70)
    
    # Check for rare categories
    rare = flag_rare_categories(df_b)
    if rare:
        print("\n⚠️  RARE CATEGORIES DETECTED:")
        for col, cats in rare.items():
            print(f"\n  {col}:")
            for cat, count in cats.items():
                pct = 100*count/len(df_b)
                print(f"    - '{cat}': {count} samples ({pct:.2f}%)")
    
    # Check for class imbalance
    imbalance = check_class_imbalance(df_b)
    print("\n⚠️  CLASS IMBALANCE ANALYSIS:")
    for col, stats in imbalance.items():
        print(f"\n  {col}:")
        print(f"    - Largest: '{stats['max_category']}' = {stats['max_pct']:.1f}%")
        print(f"    - Imbalance ratio: {stats['ratio']:.0f}:1")
        if stats['ratio'] > 50:
            print(f"    - ⚠️  SEVERE imbalance detected (>50:1)")
    
    # ==================== CONTINGENCY TABLES ====================
    print("\n" + "="*70)
    print("CONTINGENCY TABLES")
    print("="*70)
    
    ct_yso_var = pd.crosstab(df_b['YSO_CLASS'], df_b['Variability'])
    ct_lc_var = pd.crosstab(df_b['LCType'], df_b['Variability'])
    ct_yso_lc = pd.crosstab(df_b['YSO_CLASS'], df_b['LCType'])
    
    print("\n1. YSO Class vs Variability:")
    print(ct_yso_var)
    
    print("\n2. Light Curve Type vs Variability:")
    print(ct_lc_var)
    
    print("\n3. YSO Class vs Light Curve Type:")
    print(ct_yso_lc)

    # ==================== NORMALIZED TABLES ====================
    print("\n" + "="*70)
    print("NORMALIZED TABLES (Row %)")
    print("="*70)
    ct_yso_var_row = normalize_contingency(ct_yso_var, axis=1)
    ct_lc_var_row = normalize_contingency(ct_lc_var, axis=1)
    ct_yso_lc_row = normalize_contingency(ct_yso_lc, axis=1)

    print("\n1. YSO Class vs Variability (Row %):")
    print((ct_yso_var_row * 100).round(1))
    print("\n2. Light Curve Type vs Variability (Row %):")
    print((ct_lc_var_row * 100).round(1))
    print("\n3. YSO Class vs Light Curve Type (Row %):")
    print((ct_yso_lc_row * 100).round(1))

    # ==================== STATISTICAL TESTS ====================
    print("\n" + "="*70)
    print("STATISTICAL SIGNIFICANCE TESTS (Chi-Squared)")
    print("="*70)
    
    print("\n1. YSO Class vs Variability:")
    chi2_1, p1, dof1 = chi2_test(df_b['YSO_CLASS'], df_b['Variability'])
    print(f"   χ² = {chi2_1:.2f}, p-value = {p1:.2e}, DOF = {dof1}")
    print(f"   Result: {'✅ HIGHLY SIGNIFICANT' if p1 < 0.001 else '❌ NOT SIGNIFICANT'}")
    
    print("\n2. Light Curve Type vs Variability:")
    chi2_2, p2, dof2 = chi2_test(df_b['LCType'], df_b['Variability'])
    print(f"   χ² = {chi2_2:.2f}, p-value = {p2:.2e}, DOF = {dof2}")
    print(f"   Result: {'✅ HIGHLY SIGNIFICANT' if p2 < 0.001 else '❌ NOT SIGNIFICANT'}")
    
    print("\n3. YSO Class vs Light Curve Type:")
    chi2_3, p3, dof3 = chi2_test(df_b['YSO_CLASS'], df_b['LCType'])
    print(f"   χ² = {chi2_3:.2f}, p-value = {p3:.2e}, DOF = {dof3}")
    print(f"   Result: {'✅ HIGHLY SIGNIFICANT' if p3 < 0.001 else '❌ NOT SIGNIFICANT'}")
    
    # ==================== EFFECT SIZE (CRAMÉR'S V) ====================
    print("\n" + "="*70)
    print("EFFECT SIZE - CRAMÉR'S V (0-1 scale)")
    print("="*70)
    print("Interpretation: 0-0.1=negligible, 0.1-0.3=weak, 0.3-0.5=moderate, >0.5=strong")
    
    v_yso_var = cramers_v(df_b['YSO_CLASS'], df_b['Variability'])
    v_lc_var = cramers_v(df_b['LCType'], df_b['Variability'])
    v_yso_lc = cramers_v(df_b['YSO_CLASS'], df_b['LCType'])
    
    def interpret_v(v):
        if v < 0.1:
            return "negligible"
        elif v < 0.3:
            return "weak"
        elif v < 0.5:
            return "moderate"
        else:
            return "strong"
    
    print(f"\n1. YSO Class ↔ Variability:     V = {v_yso_var:.4f} ({interpret_v(v_yso_var)})")
    print(f"2. Light Curve ↔ Variability:   V = {v_lc_var:.4f} ({interpret_v(v_lc_var)})")
    print(f"3. YSO Class ↔ Light Curve:     V = {v_yso_lc:.4f} ({interpret_v(v_yso_lc)})")
    
    # ==================== METRIC CORRELATIONS ====================
    print("\n" + "="*70)
    print("NUMERIC VARIABILITY METRICS (Pearson Correlation)")
    print("="*70)
    
    numeric_cols = [
        'W2magMean', 'W2magMed', 'sig_W2Flux', 'delW2mag', 'Period',
        'slope', 'r_value', 'FLP_LSP_BOOT', 'slope_color', 'pearson_color'
    ]
    numeric_cols = [c for c in numeric_cols if c in df_b.columns]
    corr_matrix = compute_correlation_matrix(df_b, numeric_cols, standardize=True)
    print("\nCorrelation Matrix:")
    print(corr_matrix.round(3))
    
    # Find strongest correlations
    print("\nStrongest correlations (|r| > 0.3):")
    for i in range(len(corr_matrix)):
        for j in range(i+1, len(corr_matrix)):
            r = corr_matrix.iloc[i, j]
            if abs(r) > 0.3:
                print(f"  {corr_matrix.index[i]} ↔ {corr_matrix.columns[j]}: r = {r:.3f}")
    
    # ==================== COLOR-VARIABILITY PHYSICS ====================
    print("\n" + "="*70)
    print("COLOR-VARIABILITY RELATIONSHIPS")
    print("="*70)
    df_color = df_b.dropna(subset=['slope_color', 'delW2mag'])
    if len(df_color) > 0:
        color_corr = df_color[['slope_color', 'delW2mag']].corr().iloc[0, 1]
        print(f"Correlation: slope_color ↔ delW2mag = {color_corr:.3f}")
    else:
        print("No valid slope_color data available for correlation.")

    # ==================== IRREGULAR SUBTYPES ====================
    print("\n" + "="*70)
    print("IRREGULAR SUBTYPES (Physics-Based)")
    print("="*70)
    df_b['IrregularSubtype'] = df_b.apply(classify_irregular_subtype, axis=1)
    df_irreg = df_b[df_b['LCType'] == 'Irregular'].copy()
    if len(df_irreg) > 0:
        irreg_counts = df_irreg['IrregularSubtype'].value_counts()
        print(irreg_counts)
    else:
        print("No Irregular sources found after QC.")

    # ==================== GENERATE HEATMAPS ====================
    print("\n" + "="*70)
    print("GENERATING HEATMAPS")
    print("="*70)
    
    # Heatmap 1: Variability Metrics (numeric)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(f'Correlation Matrix: YSO Variability Metrics\n(Standardized, QC: N>={MIN_POINTS}, kept={len(df_b)})',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'correlation_heatmap_variability_metrics.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved correlation_heatmap_variability_metrics.png")
    
    # Heatmap 2: Normalized YSO vs Variability (row %)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(ct_yso_var_row * 100, annot=True, fmt='.1f', cmap='Blues',
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('YSO Class vs Variability (Row %)',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'heatmap_yso_vs_variability_row_norm.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved heatmap_yso_vs_variability_row_norm.png")

    # Heatmap 3: Normalized LC vs Variability (row %)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(ct_lc_var_row * 100, annot=True, fmt='.1f', cmap='Blues',
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Light Curve Type vs Variability (Row %)',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'heatmap_lc_vs_variability_row_norm.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved heatmap_lc_vs_variability_row_norm.png")

    # Heatmap 4: Pearson residuals (YSO vs Variability)
    resid_yso_var = pearson_residuals(ct_yso_var)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(resid_yso_var, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Pearson Residuals: YSO Class vs Variability',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'pearson_residuals_yso_vs_variability.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved pearson_residuals_yso_vs_variability.png")

    # Heatmap 5: Pearson residuals (LC vs Variability)
    resid_lc_var = pearson_residuals(ct_lc_var)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(resid_lc_var, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Pearson Residuals: LC Type vs Variability',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'pearson_residuals_lc_vs_variability.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved pearson_residuals_lc_vs_variability.png")

    # Heatmap 6: Pearson residuals (YSO vs LC Type)
    resid_yso_lc = pearson_residuals(ct_yso_lc)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(resid_yso_lc, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Pearson Residuals: YSO Class vs LC Type',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(str(PLOTS_DIR / 'pearson_residuals_yso_vs_lc.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved pearson_residuals_yso_vs_lc.png")

    # Heatmap 7: Irregular subtypes by YSO class (row %)
    if len(df_irreg) > 0:
        ct_irreg = pd.crosstab(df_irreg['YSO_CLASS'], df_irreg['IrregularSubtype'])
        ct_irreg_row = normalize_contingency(ct_irreg, axis=1)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(ct_irreg_row * 100, annot=True, fmt='.1f', cmap='Blues',
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Irregular Subtypes by YSO Class (Row %)',
                     fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(str(PLOTS_DIR / 'heatmap_irregular_subtypes_row_norm.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved heatmap_irregular_subtypes_row_norm.png")

    # Scatter: color slope vs variability amplitude
    if len(df_color) > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.scatterplot(data=df_color, x='delW2mag', y='slope_color',
                        hue='YSO_CLASS', alpha=0.6, ax=ax)
        ax.axhline(0, color='gray', linewidth=1, linestyle='--')
        ax.set_title('Color Slope vs Variability Amplitude\n(Positive slope = redder when fainter)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('delW2mag (amplitude)')
        ax.set_ylabel('slope_color (W1-W2 vs W2)')
        plt.tight_layout()
        plt.savefig(str(PLOTS_DIR / 'scatter_color_slope_vs_variability.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved scatter_color_slope_vs_variability.png")
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  1. correlation_heatmap_variability_metrics.png")
    print("  2. heatmap_yso_vs_variability_row_norm.png")
    print("  3. heatmap_lc_vs_variability_row_norm.png")
    print("  4. pearson_residuals_yso_vs_variability.png")
    print("  5. pearson_residuals_lc_vs_variability.png")
    print("  6. pearson_residuals_yso_vs_lc.png")
    print("  7. heatmap_irregular_subtypes_row_norm.png")
    print("  8. scatter_color_slope_vs_variability.png")


if __name__ == "__main__":
    main()
