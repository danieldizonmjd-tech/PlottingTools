import pandas as pd
import numpy as np
from pathlib import Path
from typing import List

def parse_mrt_file(filepath: str) -> pd.DataFrame:
    """
    Parse MRT table format for different paper sources.
    Handles Papers B & C format (Tab-separated with J/L prefixed objects).
    """
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()

    missing_sentinels = {'?', 'uncertain', '-9.999', '-9.99', '-99.99', '-999.9', '-999.99'}
    yso_classes = {'ClassI', 'ClassII', 'ClassIII', 'FS', 'uncertain'}

    def _to_float(val: str) -> float:
        if val is None:
            return np.nan
        v = val.strip()
        if v in missing_sentinels:
            return np.nan
        try:
            return float(v)
        except ValueError:
            return np.nan

    def _to_int(val: str):
        try:
            return int(val)
        except (ValueError, TypeError):
            return np.nan

    for line in lines:
        if line.startswith('J') or line.startswith('L'):
            parts = line.split()
            if len(parts) < 16:
                continue

            # Handle lines where SED_SLOPE is missing and YSO_CLASS is "uncertain"
            if parts[3] in yso_classes and parts[4].isdigit():
                sed_slope = np.nan
                yso_class = parts[3]
                idx = 4
            else:
                sed_slope = _to_float(parts[3])
                yso_class = parts[4]
                idx = 5

            try:
                row = {
                    'Objname': parts[0],
                    'RAdeg': _to_float(parts[1]),
                    'DEdeg': _to_float(parts[2]),
                    'SED_SLOPE': sed_slope,
                    'YSO_CLASS': yso_class,
                    'Number': _to_int(parts[idx]),
                    'W2magMean': _to_float(parts[idx + 1]),
                    'W2magMed': _to_float(parts[idx + 2]),
                    'sig_W2Flux': _to_float(parts[idx + 3]),
                    'err_W2Flux': _to_float(parts[idx + 4]),
                    'delW2mag': _to_float(parts[idx + 5]),
                    'Period': _to_float(parts[idx + 6]),
                    'FLP_LSP_BOOT': _to_float(parts[idx + 7]),
                    'slope': _to_float(parts[idx + 8]),
                    'e_slope': _to_float(parts[idx + 9]),
                    'r_value': _to_float(parts[idx + 10]),
                    'e_r_value': _to_float(parts[idx + 11]) if len(parts) > idx + 11 else np.nan,
                    'p_value': _to_float(parts[idx + 12]) if len(parts) > idx + 12 else np.nan,
                    'e_p_value': _to_float(parts[idx + 13]) if len(parts) > idx + 13 else np.nan,
                    'slope_color': _to_float(parts[idx + 14]) if len(parts) > idx + 14 else np.nan,
                    'e_slope_color': _to_float(parts[idx + 15]) if len(parts) > idx + 15 else np.nan,
                    'pearson_color': _to_float(parts[idx + 16]) if len(parts) > idx + 16 else np.nan,
                    'pvalue_color': _to_float(parts[idx + 17]) if len(parts) > idx + 17 else np.nan,
                    'LCType': parts[idx + 18] if len(parts) > idx + 18 else (parts[-1] if len(parts) > 0 else 'Unknown'),
                }
                data.append(row)
            except (ValueError, IndexError):
                continue

    return pd.DataFrame(data)

def compute_correlation_matrix(df: pd.DataFrame, columns: List[str] = None, standardize: bool = True) -> pd.DataFrame:
    """
    Compute Pearson correlation matrix for specified columns.
    Handles NaN values by dropping rows with missing data.
    
    Args:
        df: DataFrame with data
        columns: Columns to correlate. If None, uses all numeric columns
        standardize: If True, standardize (z-score) columns before correlation to prevent
                   variables with large scales from dominating
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    subset = df[columns].dropna()
    
    if standardize:
        subset = (subset - subset.mean()) / subset.std()
    
    return subset.corr()

def categorize_variability(df: pd.DataFrame, col: str = 'delW2mag') -> pd.Series:
    """
    Categorize sources by variability amplitude.
    Low: < 0.2 mag, Medium: 0.2-0.5 mag, High: > 0.5 mag
    """
    categories = []
    for val in df[col]:
        if pd.isna(val):
            categories.append('Unknown')
        elif val < 0.2:
            categories.append('Low')
        elif val < 0.5:
            categories.append('Medium')
        else:
            categories.append('High')
    return pd.Series(categories, index=df.index)

