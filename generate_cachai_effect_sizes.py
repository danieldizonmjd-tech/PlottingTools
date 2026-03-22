#!/usr/bin/env python3
"""
Generate Cachai Chord Diagrams for Effect Size Metrics
Creates chord diagrams for Cramér's V and Phi coefficient matrices
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import cachai.chplot as chp
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

import sys
sys.path.insert(0, '/Users/marcus/Desktop/YSO')
from yso_utils import parse_mrt_file, categorize_variability


def cramers_v(x, y):
    """Calculate Cramér's V statistic"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


def phi_coefficient(x, y):
    """Calculate Phi coefficient"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    return np.sqrt(chi2 / n)


def build_effect_size_matrix(df, variables, effect_func):
    """Build pairwise effect size matrix for categorical variables"""
    n_vars = len(variables)
    matrix = np.zeros((n_vars, n_vars))
    
    for i in range(n_vars):
        for j in range(n_vars):
            if i == j:
                matrix[i, j] = 1.0
            else:
                matrix[i, j] = effect_func(df[variables[i]], df[variables[j]])
    
    return pd.DataFrame(matrix, index=variables, columns=variables)


def main():
    print("Loading YSO data...")
    paper_b_file = '/Users/marcus/Desktop/YSO/paper_data_files/apjsadc397t2_mrt.txt'
    df_b = parse_mrt_file(paper_b_file)
    
    print(f"Loaded {len(df_b)} sources\n")
    df_b['Variability'] = categorize_variability(df_b, 'delW2mag')
    
    categorical_vars = ['YSO_CLASS', 'LCType', 'Variability']
    
    print("="*70)
    print("GENERATING EFFECT SIZE MATRICES")
    print("="*70)
    
    # Cramér's V Matrix
    print("\n1. Computing Cramér's V matrix...")
    cramers_matrix = build_effect_size_matrix(df_b, categorical_vars, cramers_v)
    print("Cramér's V Matrix:")
    print(cramers_matrix.round(4))
    
    # Phi Coefficient Matrix
    print("\n2. Computing Phi Coefficient matrix...")
    phi_matrix = build_effect_size_matrix(df_b, categorical_vars, phi_coefficient)
    print("Phi Coefficient Matrix:")
    print(phi_matrix.round(4))
    
    # ==================== CRAMÉR'S V CHORD DIAGRAM ====================
    print("\n" + "="*70)
    print("GENERATING CRAMÉR'S V CHORD DIAGRAM")
    print("="*70)
    
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='white')
    
    chord_plot = chp.chord(
        cramers_matrix,
        ax=ax,
        threshold=0.1,
        fontsize=12,
        chord_linewidth=1.5,
        rasterized=True
    )
    
    ax.set_title("Cramér's V: Categorical Variable Associations\n(YSO Class, Light Curve Type, Variability)",
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_cramers = '/Users/marcus/Desktop/YSO/plotting_tool_graphs/cachai_cramers_v_chord.png'
    plt.savefig(output_cramers, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: cachai_cramers_v_chord.png")
    
    # ==================== PHI COEFFICIENT CHORD DIAGRAM ====================
    print("\n" + "="*70)
    print("GENERATING PHI COEFFICIENT CHORD DIAGRAM")
    print("="*70)
    
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='white')
    
    chord_plot = chp.chord(
        phi_matrix,
        ax=ax,
        threshold=0.1,
        fontsize=12,
        chord_linewidth=1.5,
        rasterized=True
    )
    
    ax.set_title("Phi Coefficient: Categorical Variable Associations\n(YSO Class, Light Curve Type, Variability)",
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_phi = '/Users/marcus/Desktop/YSO/plotting_tool_graphs/cachai_phi_coefficient_chord.png'
    plt.savefig(output_phi, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: cachai_phi_coefficient_chord.png")
    
    # ==================== SUMMARY ====================
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nMetric Interpretations:")
    print("\nCramér's V (0-1 scale):")
    print("  0-0.1: Negligible association")
    print("  0.1-0.3: Weak association")
    print("  0.3-0.5: Moderate association")
    print("  >0.5: Strong association")
    
    print("\nPhi Coefficient (0-1 scale, similar interpretation):")
    print("  0-0.1: Negligible association")
    print("  0.1-0.3: Weak association")
    print("  0.3-0.5: Moderate association")
    print("  >0.5: Strong association")
    
    print("\nGenerated chord diagrams:")
    print(f"  1. cachai_cramers_v_chord.png")
    print(f"  2. cachai_phi_coefficient_chord.png")
    
    print("\nChord width represents effect size strength:")
    print("  - Thicker chords = stronger association between variables")
    print("  - Threshold = 0.1 (associations below 0.1 hidden)")


if __name__ == "__main__":
    main()
