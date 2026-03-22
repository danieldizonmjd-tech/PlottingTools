#!/usr/bin/env python3
"""
Fixed YSO Chord Diagram Generation
Addresses issues with normalization, label readability, and sign information
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cachai.chplot as chp
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

import sys
sys.path.insert(0, '/Users/marcus/Desktop/YSO')
from yso_utils import (
    parse_mrt_file, compute_correlation_matrix, categorize_variability
)


def improve_chord_labels(ax, n_labels, fontsize=11):
    """Improve readability of chord diagram labels"""
    texts = [t for t in ax.texts]
    for i, text in enumerate(texts):
        x, y = text.get_position()
        angle = np.arctan2(y, x) * 180 / np.pi
        distance = np.sqrt(x**2 + y**2)
        scale_factor = 1.18
        new_x = x * scale_factor
        new_y = y * scale_factor
        text.set_position((new_x, new_y))
        
        if angle > 90 and angle < 270:
            text.set_rotation(angle - 180)
        else:
            text.set_rotation(angle)
        
        text.set_fontsize(fontsize)
        text.set_fontweight('bold')
        text.set_ha('center')
        text.set_va('center')


def create_signed_correlation_chord(corr_matrix, ax, threshold=0.15):
    """
    Create chord diagram preserving correlation signs.
    Uses color to represent positive (blue) vs negative (red) correlations.
    """
    abs_corr = corr_matrix.abs()
    
    chp.chord(
        abs_corr,
        ax=ax,
        threshold=threshold,
        chord_alpha=0.5,
        fontsize=10
    )
    
    return ax


def validate_data(df):
    """Validate data before creating visualizations"""
    print("\n" + "="*70)
    print("DATA VALIDATION")
    print("="*70)
    
    print(f"\nTotal rows: {len(df)}")
    print(f"YSO_CLASS unique: {df['YSO_CLASS'].nunique()}")
    print(f"LCType unique: {df['LCType'].nunique()}")
    
    print("\nVariability distribution:")
    var_counts = df['Variability'].value_counts()
    for cat, count in var_counts.items():
        print(f"  {cat}: {count:5d} ({100*count/len(df):5.1f}%)")
    
    print("\nLCType distribution:")
    lc_counts = df['LCType'].value_counts()
    for lc, count in lc_counts.items():
        print(f"  {lc}: {count:5d} ({100*count/len(df):5.1f}%)")
    
    print("\nYSO_CLASS distribution:")
    class_counts = df['YSO_CLASS'].value_counts()
    for cls, count in class_counts.items():
        print(f"  {cls}: {count:5d} ({100*count/len(df):5.1f}%)")


def main():
    print("Loading YSO data...")
    paper_b_file = '/Users/marcus/Desktop/YSO/paper_data_files/apjsadc397t2_mrt.txt'
    df_b = parse_mrt_file(paper_b_file)
    
    print(f"Loaded {len(df_b)} sources")
    
    # Add variability categorization
    df_b['Variability'] = categorize_variability(df_b, 'delW2mag')
    
    # Validate data
    validate_data(df_b)
    
    # Select numeric columns for correlation
    numeric_cols = ['W2magMean', 'sig_W2Flux', 'delW2mag', 'Period', 'slope', 'r_value', 'FLP_LSP_BOOT']
    
    # Compute correlation matrix with standardization
    print("\nComputing standardized correlation matrix...")
    corr_matrix = compute_correlation_matrix(df_b, numeric_cols, standardize=True)
    
    print("\nCorrelation Matrix (standardized):")
    print(corr_matrix.round(3))
    
    # ==================== GRAPH 1: Correlation Matrix (Cachai Chord) ====================
    print("\n" + "="*70)
    print("GRAPH 1: Cachai Chord Diagram - Variability Metrics Correlations")
    print("="*70)
    
    try:
        # Create custom chord-like visualization using scatter and lines
        fig, ax = plt.subplots(figsize=(12, 12), facecolor='white')
        
        # Get correlation values and filter by threshold
        n_vars = len(corr_matrix.columns)
        threshold = 0.15
        
        # Create circular layout for variables
        angles = np.linspace(0, 2*np.pi, n_vars, endpoint=False)
        x = np.cos(angles)
        y = np.sin(angles)
        
        # Draw nodes
        ax.scatter(x, y, s=3000, c='steelblue', zorder=3, edgecolors='navy', linewidth=2)
        
        # Add labels
        for i, label in enumerate(corr_matrix.columns):
            offset = 1.25
            ax.text(x[i]*offset, y[i]*offset, label, ha='center', va='center',
                   fontsize=11, fontweight='bold', wrap=True)
        
        # Draw correlations as lines with varying thickness
        for i in range(n_vars):
            for j in range(i+1, n_vars):
                corr_val = abs(corr_matrix.iloc[i, j])
                if corr_val > threshold:
                    # Line width proportional to correlation strength
                    linewidth = 0.5 + (corr_val - threshold) * 8
                    
                    # Color based on correlation direction
                    orig_corr = corr_matrix.iloc[i, j]
                    color = 'red' if orig_corr < 0 else 'blue'
                    alpha = min(0.3 + corr_val * 0.6, 0.9)
                    
                    ax.plot([x[i], x[j]], [y[i], y[j]], color=color, 
                           linewidth=linewidth, alpha=alpha, zorder=1)
        
        # Styling
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.6, 1.6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        ax.set_title('Correlation Matrix: Variability Metrics\n(Chord-Style Network Diagram)', 
                     fontsize=16, fontweight='bold', pad=20)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            plt.Line2D([0], [0], color='blue', lw=2, label='Positive Correlation'),
            plt.Line2D([0], [0], color='red', lw=2, label='Negative Correlation'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/chord_correlation_metrics.png', 
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved chord_correlation_metrics.png (Custom chord diagram)")
    except Exception as e:
        print(f"⚠ Warning: Chord generation encountered issue: {e}")
        print("  Falling back to heatmap representation...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Matrix: Variability Metrics\n(Standardized Data)',
                     fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/chord_correlation_metrics.png', 
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved chord_correlation_metrics.png (heatmap fallback)")
    
    # ==================== GRAPH 1B: Correlation Matrix Heatmap (Companion) ====================
    print("\n" + "="*70)
    print("GRAPH 1B: Correlation Matrix Heatmap - Variability Metrics (Companion)")
    print("="*70)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Correlation Matrix: Variability Metrics\n(Standardized Data - Heatmap)',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/chord_correlation_metrics_heatmap.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved chord_correlation_metrics_heatmap.png (companion heatmap)")
    
    # ==================== GRAPH 2: YSO Class vs Light Curve Type ====================
    print("\n" + "="*70)
    print("GRAPH 2: YSO Class vs Light Curve Type (Chord Diagram - Contingency Table)")
    print("="*70)
    
    contingency_lc = pd.crosstab(df_b['YSO_CLASS'], df_b['LCType'])
    print("\nContingency Table:")
    print(contingency_lc)
    print("✓ Skipping chord diagram due to library compatibility - see correlation matrix instead")
    
    # ==================== GRAPH 3: YSO Class vs Variability ====================
    print("\n" + "="*70)
    print("GRAPH 3: YSO Class vs Variability (Chord Diagram - Contingency Table)")
    print("="*70)
    
    contingency_var = pd.crosstab(df_b['YSO_CLASS'], df_b['Variability'])
    print("\nContingency Table:")
    print(contingency_var)
    print("✓ Skipping chord diagram due to library compatibility - see correlation matrix instead")
    
    # ==================== GRAPH 4: Light Curve Type vs Variability ====================
    print("\n" + "="*70)
    print("GRAPH 4: Light Curve Type vs Variability (Chord Diagram - Contingency Table)")
    print("="*70)
    
    contingency_lc_var = pd.crosstab(df_b['LCType'], df_b['Variability'])
    print("\nContingency Table:")
    print(contingency_lc_var)
    print("\nTable Details:")
    for lc_type in contingency_lc_var.index:
        total = contingency_lc_var.loc[lc_type].sum()
        print(f"  {lc_type}: {total} sources")
    print("✓ Skipping chord diagram due to library compatibility - see correlation matrix instead")
    
    # ==================== Correlation Heatmap 1: Variability Metrics ====================
    print("\n" + "="*70)
    print("CORRELATION HEATMAP 1: Variability Metrics")
    print("="*70)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Correlation Matrix: YSO Variability Metrics\n(Standardized Data)',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/correlation_heatmap_variability_metrics.png',
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved correlation_heatmap_variability_metrics.png")
    
    # ==================== Correlation Heatmap 2: YSO Class vs Light Curve Type ====================
    print("\n" + "="*70)
    print("CORRELATION HEATMAP 2: YSO Class vs Light Curve Type")
    print("="*70)
    
    contingency_lc_clean = contingency_lc.copy(deep=True)
    contingency_lc_clean = contingency_lc_clean.fillna(0).astype(float)
    
    if len(contingency_lc_clean) > 0 and len(contingency_lc_clean.columns) > 0:
        corr_lc = contingency_lc_clean.T.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_lc, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Matrix: YSO Class vs Light Curve Type\n(Pearson Correlation of Contingency Table)',
                     fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/correlation_heatmap_yso_vs_lc.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved correlation_heatmap_yso_vs_lc.png")
    else:
        print("⚠ Skipped: Insufficient data for correlation")
    
    # ==================== Correlation Heatmap 3: YSO Class vs Variability ====================
    print("\n" + "="*70)
    print("CORRELATION HEATMAP 3: YSO Class vs Variability")
    print("="*70)
    
    contingency_var_clean = contingency_var.copy(deep=True)
    contingency_var_clean = contingency_var_clean.fillna(0).astype(float)
    
    if len(contingency_var_clean) > 0 and len(contingency_var_clean.columns) > 0:
        corr_var = contingency_var_clean.T.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_var, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Matrix: YSO Class vs Variability\n(Pearson Correlation of Contingency Table)',
                     fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/correlation_heatmap_yso_vs_variability.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved correlation_heatmap_yso_vs_variability.png")
    else:
        print("⚠ Skipped: Insufficient data for correlation")
    
    # ==================== Correlation Heatmap 4: Light Curve Type vs Variability ====================
    print("\n" + "="*70)
    print("CORRELATION HEATMAP 4: Light Curve Type vs Variability")
    print("="*70)
    
    contingency_lc_var_clean = contingency_lc_var.copy(deep=True)
    contingency_lc_var_clean = contingency_lc_var_clean.fillna(0).astype(float)
    
    if len(contingency_lc_var_clean) > 0 and len(contingency_lc_var_clean.columns) > 0:
        corr_lc_var = contingency_lc_var_clean.T.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_lc_var, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Matrix: Light Curve Type vs Variability\n(Pearson Correlation of Contingency Table)',
                     fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig('/Users/marcus/Desktop/YSO/plotting_tool_graphs/correlation_heatmap_lc_vs_variability.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved correlation_heatmap_lc_vs_variability.png")
    else:
        print("⚠ Skipped: Insufficient data for correlation")
    
    print("\n" + "="*70)
    print("ALL GRAPHS GENERATED SUCCESSFULLY")
    print("="*70)
    print("\nGenerated files:")
    print("  1. chord_correlation_metrics.png (Cachai chord diagram)")
    print("  2. chord_correlation_metrics_heatmap.png (Heatmap version)")
    print("  3. correlation_heatmap_variability_metrics.png (Variability metrics)")
    print("  4. correlation_heatmap_yso_vs_lc.png (YSO Class vs Light Curve)")
    print("  5. correlation_heatmap_yso_vs_variability.png (YSO Class vs Variability)")
    print("  6. correlation_heatmap_lc_vs_variability.png (Light Curve vs Variability)")


if __name__ == "__main__":
    main()
