# PlottingTools: YSO Variability Summary Pipeline

This repo takes a published YSO catalog table and generates a small, reliable set of plots that summarize:
- How variability amplitude relates to light curve morphology (LCType)
- How variability relates to evolutionary class (YSO_CLASS)
- Whether results are being driven by measurement noise or sample imbalance

The goal is quality over quantity: one clear analysis path, a small evidence set, and documentation that tells you what to believe.

## Broad overview

Input:
- `paper_data_files/apjsadc397t2_mrt.txt` (Paper B table)

Core outputs:
- Saved into `plotting_tool_graphs/`
- A short list of plots intended to be the primary evidence set

Archived material:
- Older scripts, one-off analyses, and legacy plots are moved into `archive/` and `plotting_tool_graphs/archive/`

## What to run (the basic path)

1. Run the core analysis
- `python3 run_analysis.py`

Outputs to look at first in `plotting_tool_graphs/`:
- `statistical_summary.png`
- `heatmap_lc_vs_variability_row_norm.png`
- `pearson_residuals_lc_vs_variability.png`
- `heatmap_yso_vs_variability_row_norm.png`
- `pearson_residuals_yso_vs_variability.png`
- `correlation_heatmap_variability_metrics.png`

This also generates the noise and selection checks:
- `scatter_dispersion_vs_median_mag.png`
- `scatter_dispersion_over_error_vs_median_mag.png`

## What to believe (and what not to over-trust)

Trust most:
- Row-normalized heatmaps: they compare category fractions fairly even with imbalanced class counts.
  - `heatmap_lc_vs_variability_row_norm.png`
  - `heatmap_yso_vs_variability_row_norm.png`
- Pearson residual heatmaps: they show which specific cells are enriched or depleted, not just that a relationship exists.
  - `pearson_residuals_lc_vs_variability.png`
  - `pearson_residuals_yso_vs_variability.png`
- `statistical_summary.png`: one-page summary of significance, effect sizes, and class imbalance.

Use with caution:
- Any result dominated by rare categories (very small counts). Those cells can look extreme even when the underlying estimate is fragile.
- “Contingency correlation” heatmaps from older scripts: they are about distribution similarity, not a primary effect size.

Archive or presentation only:
- `chord_*.png` and older correlation heatmaps produced by `YSO_Chord_Project.ipynb` or `generate_fixed_visualizations.py`.

## The big picture of what the plots are doing

This analysis has three layers:

1. Categorical relationships
- Build contingency tables (YSO class, LCType, variability bin).
- Show fair comparisons via row-normalized heatmaps.
- Show which cells drive the patterns via Pearson residuals.

2. Numeric metric sanity checks
- Compute correlations among numeric variability metrics to understand redundancy and coupling.
- This prevents over-interpreting two “different” metrics that are actually measuring the same thing.

3. Photometric noise checks
- Scatter plots versus median magnitude show where noise floors and brightness effects can bias variability diagnostics.

## What to do with the results

Use this flow when writing conclusions:

1. Start with `statistical_summary.png` to ground significance, effect sizes, and imbalance.
2. Use row-normalized heatmaps to state population-level trends.
3. Use Pearson residual maps to cite the specific enriched or depleted category pairs.
4. Use dispersion plots to show you accounted for noise and magnitude dependence.

## Where the detailed documentation is

- Plot-by-plot meanings and code locations: `plotting_tool_graphs/README_PLOT_GUIDE.md`
- Short conclusions from the plots: `plotting_tool_graphs/CONCLUSIONS.md`
- Older, detailed notes (archived): `archive/docs/`

## Repo organization note

This repo intentionally keeps a small core in the root folder.
Older scripts, one-off analysis, and legacy plots are moved into `archive/` and `plotting_tool_graphs/archive/` to keep the main path easy to follow.
