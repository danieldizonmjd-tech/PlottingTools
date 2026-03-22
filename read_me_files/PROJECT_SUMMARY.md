# YSO Variability Analysis — Project Summary

## Overview
This repo analyzes mid‑infrared YSO variability using Paper B (apjsadc397t2_mrt.txt) and focuses on physics‑meaningful distributions instead of raw‑count “pretty” plots. The updated workflow emphasizes normalized contingency tables, Pearson residuals, and color‑slope diagnostics to connect variability behavior to dust vs accretion.

## Data Scope
- **Catalog**: Paper B (Illuminating Youth: mid‑IR variability)
- **Sample size (after QC)**: 20,893 sources
- **QC**: `Number >= 10`, finite core metrics (`W2magMean`, `sig_W2Flux`, `delW2mag`, `Period`, `slope`, `r_value`, `FLP_LSP_BOOT`)

## Key Outputs (Regenerate with one command)
Run:
```bash
python generate_improved_visualizations.py
```
Key figures written to `plotting_tool_graphs/`:
- `heatmap_yso_vs_variability_row_norm.png`
- `heatmap_lc_vs_variability_row_norm.png`
- `pearson_residuals_yso_vs_variability.png`
- `pearson_residuals_lc_vs_variability.png`
- `pearson_residuals_yso_vs_lc.png`
- `heatmap_irregular_subtypes_row_norm.png`
- `scatter_color_slope_vs_variability.png`
- `correlation_heatmap_variability_metrics.png`

Optional: `python generate_comprehensive_visualizations.py` to reproduce the normalized + residual heatmaps and statistical summary figure.

## Headline Findings (from current run)
- **Class imbalance is real**: Class II dominates counts (61.1%), but the **normalized** view shows different behavior by class.
- **YSO class vs variability is weak** (Cramér’s V = 0.108). **LCType vs variability is moderate** (V = 0.385), meaning light‑curve morphology explains much more of the amplitude distribution than evolutionary class alone.
- **Irregular and Burst light curves are strongly enriched in high variability**; NV is strongly enriched in low/medium.
- **Color‑slope vs amplitude is weak** (r ≈ 0.049), so “more variable” doesn’t automatically imply stronger color evolution.
- **Irregular subtypes separate into physical regimes** using color slope:
  - Accretor‑like (bluer when brighter), Fader‑like (redder when fainter), and Stochastic/low‑signal.

## Quick Interpretation
The dataset is dominated by Class II sources, but morphology (Irregular/Burst/Drop vs NV) is a more direct handle on physical variability mechanisms. Color slope adds the missing physics: positive slope suggests extinction, negative slope suggests accretion hotspots. The resulting picture is more astrophysical than the old chord‑diagram view of raw counts.
