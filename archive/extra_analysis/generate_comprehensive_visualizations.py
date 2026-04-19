#!/usr/bin/env python3
"""
Comprehensive YSO Statistical Visualizations
Includes: contingency tables, effect sizes, confidence intervals, matplotlib chord diagrams
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, chi2
from matplotlib.patches import Wedge, FancyBboxPatch
from matplotlib.patches import ConnectionPatch
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

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
    # Drop rows with NaNs in the fields we use later
    numeric_cols = ['W2magMean', 'sig_W2Flux', 'delW2mag', 'Period', 'slope', 'r_value', 'FLP_LSP_BOOT']
    present = [c for c in numeric_cols if c in keep.columns]
    if present:
        keep = keep.replace([np.inf, -np.inf], np.nan)
        keep = keep.dropna(subset=present)
    return keep


def cramers_v_with_ci(x, y, confidence=0.95):
    """Calculate Cramér's V with bootstrap confidence interval"""
    confusion_matrix = pd.crosstab(x, y)
    chi2_stat = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    
    if min_dim == 0:
        return 0, (0, 0)
    
    v = np.sqrt(chi2_stat / (n * min_dim))
    
    # Bootstrap CI
    np.random.seed(42)
    v_bootstrap = []
    for _ in range(1000):
        indices = np.random.choice(len(x), size=len(x), replace=True)
        x_boot = x.iloc[indices].values
        y_boot = y.iloc[indices].values
        cm_boot = pd.crosstab(x_boot, y_boot)
        chi2_boot = chi2_contingency(cm_boot)[0]
        v_boot = np.sqrt(chi2_boot / (len(x) * min_dim)) if min_dim > 0 else 0
        v_bootstrap.append(v_boot)
    
    v_bootstrap = np.array(v_bootstrap)
    alpha = (1 - confidence) / 2
    ci_lower = np.percentile(v_bootstrap, alpha * 100)
    ci_upper = np.percentile(v_bootstrap, (1 - alpha) * 100)
    
    return v, (ci_lower, ci_upper)


def phi_coefficient(x, y):
    """Calculate Phi coefficient (effect size for 2x2 tables, approximation for larger)"""
    confusion_matrix = pd.crosstab(x, y)
    chi2_stat = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    
    # Phi is chi2/n
    phi = np.sqrt(chi2_stat / n)
    return phi


def create_heatmap_with_contingency(contingency_table, title, filename, metric='pearson'):
    """Create heatmap with contingency table embedded"""
    if metric == 'pearson':
        data = contingency_table.astype(float).T.corr()
    else:
        data = contingency_table
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create heatmap
    sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1.5, cbar_kws={"shrink": 0.8}, ax=ax,
                annot_kws={'size': 10, 'weight': 'bold'})
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add contingency table as text box
    ct_text = "Contingency Table:\n" + contingency_table.to_string()
    fig.text(0.02, 0.02, ct_text, fontsize=8, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


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


def create_normalized_heatmap(table: pd.DataFrame, title: str, filename: str):
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(table * 100, annot=True, fmt='.1f', cmap='Blues',
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_residual_heatmap(table: pd.DataFrame, title: str, filename: str):
    residuals = pearson_residuals(table)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(residuals, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_statistical_summary(stats_dict, filename):
    """Create comprehensive statistical summary figure"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Statistical Summary: YSO Categorical Associations', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Panel 1: Chi-squared results
    ax = axes[0, 0]
    ax.axis('off')
    chi2_text = "Chi-Squared Tests of Independence\n" + "="*50 + "\n\n"
    for name, stats in stats_dict['chi2_tests'].items():
        chi2_text += f"{name}:\n"
        chi2_text += f"  χ² = {stats['chi2']:.2f}\n"
        chi2_text += f"  p-value = {stats['p_value']:.2e}\n"
        chi2_text += f"  DOF = {stats['dof']}\n"
        chi2_text += f"  Result: {'✓ SIGNIFICANT' if stats['p_value'] < 0.001 else '✗ NOT SIGNIFICANT'}\n\n"
    
    ax.text(0.05, 0.95, chi2_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Panel 2: Cramér's V with CI
    ax = axes[0, 1]
    ax.axis('off')
    cramers_text = "Cramér's V Effect Sizes (with 95% CI)\n" + "="*50 + "\n\n"
    for name, stats in stats_dict['cramers_v'].items():
        v, ci = stats['v'], stats['ci']
        if v < 0.1:
            effect = "negligible"
        elif v < 0.3:
            effect = "weak"
        elif v < 0.5:
            effect = "moderate"
        else:
            effect = "strong"
        
        cramers_text += f"{name}:\n"
        cramers_text += f"  V = {v:.4f} [{ci[0]:.4f}, {ci[1]:.4f}]\n"
        cramers_text += f"  Effect: {effect}\n\n"
    
    ax.text(0.05, 0.95, cramers_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    # Panel 3: Phi Coefficients
    ax = axes[1, 0]
    ax.axis('off')
    phi_text = "Phi Coefficient (Standardized Effect Size)\n" + "="*50 + "\n\n"
    for name, phi in stats_dict['phi'].items():
        phi_text += f"{name}: φ = {phi:.4f}\n"
    
    ax.text(0.05, 0.95, phi_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
    
    # Panel 4: Sample size & imbalance
    ax = axes[1, 1]
    ax.axis('off')
    sample_text = "Sample Size & Class Imbalance\n" + "="*50 + "\n\n"
    for name, counts in stats_dict['imbalance'].items():
        sample_text += f"{name}:\n"
        sample_text += f"  N = {counts['total']}\n"
        sample_text += f"  Max category: {counts['max_pct']:.1f}%\n"
        sample_text += f"  Imbalance ratio: {counts['ratio']:.0f}:1\n"
        if counts['ratio'] > 50:
            sample_text += f"  ⚠️ SEVERE imbalance\n"
        sample_text += "\n"
    
    ax.text(0.05, 0.95, sample_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.2))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_matplotlib_chord(contingency_table, title, filename, threshold=0.001):
    """Create a matplotlib-based chord diagram from contingency table"""
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
    
    # Get categories
    cats1 = list(contingency_table.index)
    cats2 = list(contingency_table.columns)
    all_cats = cats1 + cats2
    n_cats = len(all_cats)
    
    # Normalize data
    data = contingency_table.astype(float)
    data_max = data.max().max()
    if data_max > 0:
        data_norm = data / data_max
    else:
        data_norm = data
    
    # Create angles for each category
    angles = np.linspace(0, 2*np.pi, n_cats, endpoint=False)
    
    # Draw nodes (category segments)
    colors1 = plt.cm.Set3(np.linspace(0, 1, len(cats1)))
    colors2 = plt.cm.Set2(np.linspace(0, 1, len(cats2)))
    
    node_colors = np.concatenate([colors1, colors2])
    node_sizes = []
    
    for i, cat in enumerate(all_cats):
        if i < len(cats1):
            size = contingency_table.iloc[i].sum()
        else:
            size = contingency_table.iloc[:, i-len(cats1)].sum()
        node_sizes.append(size)
    
    # Normalize node sizes for visualization
    node_sizes_norm = np.array(node_sizes) / max(node_sizes) * 0.3
    
    # Draw connections (chords)
    for i, cat1 in enumerate(cats1):
        for j, cat2 in enumerate(cats2):
            value = data_norm.iloc[i, j]
            
            if value > threshold:
                angle1 = angles[i]
                angle2 = angles[len(cats1) + j]
                
                # Draw connection
                theta = np.linspace(angle1, angle2, 100)
                r = 0.8 + 0.1 * value
                
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                
                alpha = 0.3 + 0.4 * value
                ax.plot(x, y, color=colors1[i], alpha=alpha, linewidth=2*value)
    
    # Draw node labels
    for i, cat in enumerate(all_cats):
        angle = angles[i]
        x = 1.2 * np.cos(angle)
        y = 1.2 * np.sin(angle)
        
        # Rotate text for readability
        rotation = np.degrees(angle)
        if angle > np.pi:
            rotation = rotation + 180
        
        ax.text(angle, 1.35, cat, ha='center', va='center', fontsize=10,
                rotation=rotation, weight='bold')
    
    ax.set_ylim(0, 2)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_zoomed_chord_rare_categories(contingency_table, title, filename):
    """Create chord diagrams focused on rare categories by filtering out dominant ones"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.suptitle(f'{title} - Rare Categories Focus', fontsize=16, fontweight='bold')
    
    # Helper function to create focused chord
    def make_focused_chord(ct, ax, min_count=None):
        cats1 = list(ct.index)
        cats2 = list(ct.columns)
        all_cats = cats1 + cats2
        n_cats = len(all_cats)
        
        data = ct.astype(float)
        data_max = data.max().max()
        if data_max > 0:
            data_norm = data / data_max
        else:
            data_norm = data
        
        angles = np.linspace(0, 2*np.pi, n_cats, endpoint=False)
        colors1 = plt.cm.Set3(np.linspace(0, 1, len(cats1)))
        colors2 = plt.cm.Set2(np.linspace(0, 1, len(cats2)))
        node_colors = np.concatenate([colors1, colors2])
        
        for i, cat1 in enumerate(cats1):
            for j, cat2 in enumerate(cats2):
                value = data_norm.iloc[i, j]
                
                if value > 0.001:
                    angle1 = angles[i]
                    angle2 = angles[len(cats1) + j]
                    
                    theta = np.linspace(angle1, angle2, 100)
                    r = 0.8 + 0.1 * value
                    
                    x = r * np.cos(theta)
                    y = r * np.sin(theta)
                    
                    alpha = 0.3 + 0.4 * value
                    ax.plot(x, y, color=colors1[i], alpha=alpha, linewidth=2*value)
        
        for i, cat in enumerate(all_cats):
            angle = angles[i]
            x = 1.2 * np.cos(angle)
            y = 1.2 * np.sin(angle)
            
            rotation = np.degrees(angle)
            if angle > np.pi:
                rotation = rotation + 180
            
            ax.text(angle, 1.35, cat, ha='center', va='center', fontsize=9,
                    rotation=rotation, weight='bold')
        
        ax.set_ylim(0, 2)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f'Threshold: {min_count}', fontsize=10)
    
    # Panel 1: All data
    ax = axes[0, 0]
    ax.set_projection('polar')
    make_focused_chord(contingency_table, ax, 'All data')
    
    # Panel 2: Only rows with count < median
    row_totals = contingency_table.sum(axis=1)
    median_row = row_totals.median()
    rare_rows = contingency_table[row_totals < median_row]
    if len(rare_rows) > 0:
        ax = axes[0, 1]
        ax.set_projection('polar')
        make_focused_chord(rare_rows, ax, f'Row count < {median_row:.0f}')
    
    # Panel 3: Only columns with count < median
    col_totals = contingency_table.sum(axis=0)
    median_col = col_totals.median()
    rare_cols = contingency_table[[c for c in contingency_table.columns if col_totals[c] < median_col]]
    if len(rare_cols.columns) > 0:
        ax = axes[1, 0]
        ax.set_projection('polar')
        make_focused_chord(rare_cols, ax, f'Col count < {median_col:.0f}')
    
    # Panel 4: Only rare in both dimensions
    rare_both = contingency_table.loc[rare_rows.index, rare_cols.columns]
    if len(rare_both) > 0 and len(rare_both.columns) > 0:
        ax = axes[1, 1]
        ax.set_projection('polar')
        make_focused_chord(rare_both, ax, 'Both dimensions rare')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    print("Loading YSO data...")
    paper_b_file = str(DATA_DIR / 'illuminating_youth_mid_ir_variability_color_evolution_mrt.txt')
    df_b = parse_mrt_file(paper_b_file)
    print(f"Loaded {len(df_b)} sources (raw)\n")

    df_b = apply_qc_paper_b(df_b, min_points=MIN_POINTS)
    print(f"Kept {len(df_b)} sources after QC (Number >= {MIN_POINTS} and finite metrics)\n")

    df_b['Variability'] = categorize_variability(df_b, 'delW2mag')
    
    # ==================== CONTINGENCY TABLES ====================
    print("="*70)
    print("COMPUTING CONTINGENCY TABLES & STATISTICS")
    print("="*70)
    
    ct_yso_var = pd.crosstab(df_b['YSO_CLASS'], df_b['Variability'])
    ct_lc_var = pd.crosstab(df_b['LCType'], df_b['Variability'])
    ct_yso_lc = pd.crosstab(df_b['YSO_CLASS'], df_b['LCType'])
    
    # ==================== STATISTICAL TESTS ====================
    print("\n1. Chi-Squared Tests")
    
    chi2_1, p1, dof1, _ = chi2_contingency(ct_yso_var)
    chi2_2, p2, dof2, _ = chi2_contingency(ct_lc_var)
    chi2_3, p3, dof3, _ = chi2_contingency(ct_yso_lc)
    
    print(f"   YSO vs Variability: χ² = {chi2_1:.2f}, p = {p1:.2e}")
    print(f"   LC vs Variability:  χ² = {chi2_2:.2f}, p = {p2:.2e}")
    print(f"   YSO vs LC Type:     χ² = {chi2_3:.2f}, p = {p3:.2e}")
    
    # ==================== EFFECT SIZES ====================
    print("\n2. Cramér's V with Confidence Intervals (95%)")
    
    v_yso_var, ci_yso_var = cramers_v_with_ci(df_b['YSO_CLASS'], df_b['Variability'])
    v_lc_var, ci_lc_var = cramers_v_with_ci(df_b['LCType'], df_b['Variability'])
    v_yso_lc, ci_yso_lc = cramers_v_with_ci(df_b['YSO_CLASS'], df_b['LCType'])
    
    print(f"   YSO vs Variability: V = {v_yso_var:.4f} [{ci_yso_var[0]:.4f}, {ci_yso_var[1]:.4f}]")
    print(f"   LC vs Variability:  V = {v_lc_var:.4f} [{ci_lc_var[0]:.4f}, {ci_lc_var[1]:.4f}]")
    print(f"   YSO vs LC Type:     V = {v_yso_lc:.4f} [{ci_yso_lc[0]:.4f}, {ci_yso_lc[1]:.4f}]")
    
    # ==================== PHI COEFFICIENTS ====================
    print("\n3. Phi Coefficients")
    
    phi_yso_var = phi_coefficient(df_b['YSO_CLASS'], df_b['Variability'])
    phi_lc_var = phi_coefficient(df_b['LCType'], df_b['Variability'])
    phi_yso_lc = phi_coefficient(df_b['YSO_CLASS'], df_b['LCType'])
    
    print(f"   YSO vs Variability: φ = {phi_yso_var:.4f}")
    print(f"   LC vs Variability:  φ = {phi_lc_var:.4f}")
    print(f"   YSO vs LC Type:     φ = {phi_yso_lc:.4f}")
    
    # ==================== SAMPLE SIZE IMBALANCE ====================
    print("\n4. Class Imbalance Analysis")
    
    def get_imbalance_stats(series):
        counts = series.value_counts()
        return {
            'total': len(series),
            'max_pct': 100*counts.max()/len(series),
            'ratio': counts.max()/counts.min()
        }
    
    imbalance_yso = get_imbalance_stats(df_b['YSO_CLASS'])
    imbalance_lc = get_imbalance_stats(df_b['LCType'])
    imbalance_var = get_imbalance_stats(df_b['Variability'])
    
    print(f"   YSO_CLASS: max={imbalance_yso['max_pct']:.1f}%, ratio={imbalance_yso['ratio']:.0f}:1")
    print(f"   LCType:    max={imbalance_lc['max_pct']:.1f}%, ratio={imbalance_lc['ratio']:.0f}:1")
    print(f"   Variability: max={imbalance_var['max_pct']:.1f}%, ratio={imbalance_var['ratio']:.1f}:1")
    
    # ==================== GENERATE VISUALIZATIONS ====================
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # 1. Normalized heatmaps (row %)
    print("\n1. Creating normalized heatmaps (row %)...")
    ct_yso_var_row = normalize_contingency(ct_yso_var, axis=1)
    ct_lc_var_row = normalize_contingency(ct_lc_var, axis=1)
    ct_yso_lc_row = normalize_contingency(ct_yso_lc, axis=1)

    create_normalized_heatmap(
        ct_yso_var_row,
        f'YSO Class vs Variability (Row %)\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'heatmap_yso_var_row_norm.png')
    )
    print("   ✓ heatmap_yso_var_row_norm.png")

    create_normalized_heatmap(
        ct_lc_var_row,
        f'Light Curve Type vs Variability (Row %)\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'heatmap_lc_var_row_norm.png')
    )
    print("   ✓ heatmap_lc_var_row_norm.png")

    create_normalized_heatmap(
        ct_yso_lc_row,
        f'YSO Class vs Light Curve Type (Row %)\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'heatmap_yso_lc_row_norm.png')
    )
    print("   ✓ heatmap_yso_lc_row_norm.png")

    # 2. Pearson residual heatmaps
    print("\n2. Creating Pearson residual heatmaps...")
    create_residual_heatmap(
        ct_yso_var,
        f'Pearson Residuals: YSO Class vs Variability\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'pearson_residuals_yso_var.png')
    )
    print("   ✓ pearson_residuals_yso_var.png")

    create_residual_heatmap(
        ct_lc_var,
        f'Pearson Residuals: Light Curve Type vs Variability\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'pearson_residuals_lc_var.png')
    )
    print("   ✓ pearson_residuals_lc_var.png")

    create_residual_heatmap(
        ct_yso_lc,
        f'Pearson Residuals: YSO Class vs Light Curve Type\n(QC: N>={MIN_POINTS}, kept={len(df_b)})',
        str(PLOTS_DIR / 'pearson_residuals_yso_lc.png')
    )
    print("   ✓ pearson_residuals_yso_lc.png")
    
    # 3. Statistical summary
    print("\n3. Creating statistical summary figure...")
    
    stats_dict = {
        'chi2_tests': {
            'YSO vs Variability': {'chi2': chi2_1, 'p_value': p1, 'dof': dof1},
            'LC vs Variability': {'chi2': chi2_2, 'p_value': p2, 'dof': dof2},
            'YSO vs LC Type': {'chi2': chi2_3, 'p_value': p3, 'dof': dof3}
        },
        'cramers_v': {
            'YSO vs Variability': {'v': v_yso_var, 'ci': ci_yso_var},
            'LC vs Variability': {'v': v_lc_var, 'ci': ci_lc_var},
            'YSO vs LC Type': {'v': v_yso_lc, 'ci': ci_yso_lc}
        },
        'phi': {
            'YSO vs Variability': phi_yso_var,
            'LC vs Variability': phi_lc_var,
            'YSO vs LC Type': phi_yso_lc
        },
        'imbalance': {
            'YSO_CLASS': imbalance_yso,
            'LCType': imbalance_lc,
            'Variability': imbalance_var
        }
    }
    
    create_statistical_summary(stats_dict,
        str(PLOTS_DIR / 'statistical_summary.png'))
    print("   ✓ statistical_summary.png")
    
    # ==================== SUMMARY ====================
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print("\nNew files created:")
    print("  Normalized heatmaps (row %):")
    print("    - heatmap_yso_var_row_norm.png")
    print("    - heatmap_lc_var_row_norm.png")
    print("    - heatmap_yso_lc_row_norm.png")
    print("  Pearson residual heatmaps:")
    print("    - pearson_residuals_yso_var.png")
    print("    - pearson_residuals_lc_var.png")
    print("    - pearson_residuals_yso_lc.png")
    print("  Summary:")
    print("    - statistical_summary.png")


if __name__ == "__main__":
    main()
