#!/usr/bin/env python3
"""
Comprehensive Data Verification and Analysis Correctness Check
"""

import pandas as pd
import numpy as np
from yso_utils import parse_mrt_file, compute_correlation_matrix, categorize_variability

def verify_data_integrity():
    """Verify data loading and completeness"""
    print("\n" + "="*70)
    print("1. DATA INTEGRITY VERIFICATION")
    print("="*70)
    
    df = parse_mrt_file('paper_data_files/apjsadc397t2_mrt.txt')
    df['Variability'] = categorize_variability(df, 'delW2mag')
    
    # Check counts
    assert len(df) == 20654, f"Expected 20654 sources, got {len(df)}"
    print(f"✓ Total sources: {len(df)}")
    
    # Check columns
    required_cols = ['RAdeg', 'DEdeg', 'W2magMean', 'sig_W2Flux', 'delW2mag', 
                     'YSO_CLASS', 'LCType', 'Variability']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    print(f"✓ All required columns present: {len(df.columns)} total")
    
    # Check for NaN values
    nan_total = df.isna().sum().sum()
    assert nan_total == 0, f"Found {nan_total} NaN values"
    print(f"✓ No NaN values (data complete)")
    
    return df

def verify_statistics(df):
    """Verify dataset statistics match expected values"""
    print("\n" + "="*70)
    print("2. STATISTICAL VALIDATION")
    print("="*70)
    
    # YSO Class distribution
    yso_dist = df['YSO_CLASS'].value_counts()
    expected_yso = {
        'ClassII': 12757,
        'FS': 4070,
        'ClassI': 2089,
        'ClassIII': 1659,
        'uncertain': 79
    }
    print("\nYSO Class Distribution:")
    for cls, expected_count in expected_yso.items():
        actual_count = yso_dist.get(cls, 0)
        assert actual_count == expected_count, f"YSO_CLASS {cls}: expected {expected_count}, got {actual_count}"
        pct = 100 * actual_count / len(df)
        print(f"  ✓ {cls}: {actual_count} ({pct:.1f}%)")
    
    # Variability distribution
    var_dist = df['Variability'].value_counts()
    expected_var = {
        'Medium': 10941,
        'High': 4907,
        'Low': 4806
    }
    print("\nVariability Distribution:")
    for var_cat, expected_count in expected_var.items():
        actual_count = var_dist.get(var_cat, 0)
        assert actual_count == expected_count, f"Variability {var_cat}: expected {expected_count}, got {actual_count}"
        pct = 100 * actual_count / len(df)
        print(f"  ✓ {var_cat}: {actual_count} ({pct:.1f}%)")
    
    # Brightness statistics
    w2_mean = df['W2magMean'].mean()
    w2_std = df['W2magMean'].std()
    assert 10.6 < w2_mean < 10.65, f"W2magMean: expected ~10.63, got {w2_mean:.2f}"
    assert 1.47 < w2_std < 1.49, f"W2magMean std: expected ~1.48, got {w2_std:.2f}"
    print(f"\nBrightness (W2 band):")
    print(f"  ✓ Mean: {w2_mean:.2f} ± {w2_std:.2f} mag")
    
    # Variability statistics
    var_mean = df['delW2mag'].mean()
    var_std = df['delW2mag'].std()
    assert 0.39 < var_mean < 0.41, f"delW2mag: expected ~0.40, got {var_mean:.2f}"
    assert 0.29 < var_std < 0.31, f"delW2mag std: expected ~0.30, got {var_std:.2f}"
    print(f"Variability (ΔW2mag):")
    print(f"  ✓ Mean: {var_mean:.2f} ± {var_std:.2f} mag")

def verify_correlations(df):
    """Verify correlation analysis is correct"""
    print("\n" + "="*70)
    print("3. CORRELATION ANALYSIS VERIFICATION")
    print("="*70)
    
    numeric_cols = ['W2magMean', 'sig_W2Flux', 'delW2mag', 'Period', 'slope', 'r_value', 'FLP_LSP_BOOT']
    corr = compute_correlation_matrix(df, numeric_cols, standardize=True)
    
    # Expected top correlations
    expected_corr = {
        ('sig_W2Flux', 'delW2mag'): 0.437,
        ('W2magMean', 'sig_W2Flux'): -0.366,
        ('sig_W2Flux', 'slope'): -0.300,
    }
    
    print("\nTop Correlations:")
    for (var1, var2), expected_r in expected_corr.items():
        actual_r = corr.loc[var1, var2]
        assert abs(actual_r - expected_r) < 0.01, f"{var1}-{var2}: expected r={expected_r:.3f}, got r={actual_r:.3f}"
        print(f"  ✓ {var1} ↔ {var2}: r = {actual_r:.3f}")
    
    # Check correlation matrix is symmetric
    is_symmetric = np.allclose(corr.values, corr.values.T)
    assert is_symmetric, "Correlation matrix is not symmetric"
    print(f"\n  ✓ Correlation matrix is symmetric")
    
    # Check diagonal is all 1s
    diag_all_ones = np.allclose(np.diag(corr.values), 1.0)
    assert diag_all_ones, "Correlation matrix diagonal is not all 1s"
    print(f"  ✓ Correlation matrix diagonal all = 1.0")

def verify_representation(df):
    """Verify data representation and categorization"""
    print("\n" + "="*70)
    print("4. DATA REPRESENTATION VERIFICATION")
    print("="*70)
    
    # Check light curve types
    lc_types = df['LCType'].unique()
    expected_lc = {'NV', 'Irregular', 'Curved', 'Burst', 'Linear', 'Periodic', 'Drop'}
    assert set(lc_types) == expected_lc, f"Unexpected light curve types: {set(lc_types)}"
    print(f"\nLight Curve Types (n={len(lc_types)}):")
    lc_dist = df['LCType'].value_counts()
    for lc_type, count in lc_dist.items():
        pct = 100 * count / len(df)
        print(f"  ✓ {lc_type}: {count:5d} ({pct:5.1f}%)")
    
    # Check variability categorization boundaries
    print(f"\nVariability Categorization:")
    low = df[df['delW2mag'] < 0.2]
    medium = df[(df['delW2mag'] >= 0.2) & (df['delW2mag'] < 0.5)]
    high = df[df['delW2mag'] >= 0.5]
    
    assert len(low) == (df['Variability'] == 'Low').sum(), "Low variability count mismatch"
    assert len(medium) == (df['Variability'] == 'Medium').sum(), "Medium variability count mismatch"
    assert len(high) == (df['Variability'] == 'High').sum(), "High variability count mismatch"
    
    print(f"  ✓ Low  (Δmag < 0.2): {len(low)} sources")
    print(f"  ✓ Medium (0.2 ≤ Δmag < 0.5): {len(medium)} sources")
    print(f"  ✓ High (Δmag ≥ 0.5): {len(high)} sources")
    
    # Verify coordinate ranges
    print(f"\nCoordinate Ranges:")
    print(f"  ✓ RA:  {df['RAdeg'].min():.1f}° to {df['RAdeg'].max():.1f}°")
    print(f"  ✓ Dec: {df['DEdeg'].min():.1f}° to {df['DEdeg'].max():.1f}°")

def main():
    print("\n" + "="*70)
    print("YSO CHORD PROJECT - COMPREHENSIVE DATA VERIFICATION")
    print("="*70)
    
    # Run all verifications
    df = verify_data_integrity()
    verify_statistics(df)
    verify_correlations(df)
    verify_representation(df)
    
    print("\n" + "="*70)
    print("✓ ALL VERIFICATIONS PASSED")
    print("="*70)
    print("\nData is valid and ready for analysis:")
    print("  - 20,654 sources loaded with no missing values")
    print("  - Statistical distributions match expected values")
    print("  - Correlation analysis is correct and consistent")
    print("  - Data representation and categorization validated")
    print("  - Chord visualization can proceed with confidence")
    print("\n")

if __name__ == "__main__":
    main()
