# YSO Plotting Tools Master Guide

This is the top level guide to the repository. It tells you what to run, where the outputs live, and where to find documentation.

## What this repo does

- Parses YSO data tables from `paper_data_files/`
- Computes variability metrics and category summaries
- Generates analysis plots into `plotting_tool_graphs/`
- Provides interpretive docs and conclusions

## Quick start

1. Generate the main plots
- `python generate_improved_visualizations.py`
- `python generate_dispersion_vs_median_plots.py`

2. Optional additional plots
- `python generate_comprehensive_visualizations.py`
- `python generate_lightcurve_qc_plots.py`

3. Generate the plot tables
- `python tools/generate_tables.py`

## Where the documentation lives

- Plot guide and meanings
  - `plotting_tool_graphs/README_PLOT_GUIDE.md`
- Conclusions summary
  - `plotting_tool_graphs/CONCLUSIONS.md`
- Validation and analysis notes
  - `VISUALIZATION_ANALYSIS.md`
  - `COMPREHENSIVE_IMPROVEMENTS.md`

## Folder map

- `paper_data_files/` raw input tables
- `plotting_tool_graphs/` output images and plot docs
- `tools/` helper scripts for tables and utilities
- `culled_csvs/` filtered subsets
- `ztf_analysis/` ZTF analysis outputs
- `ztf_candidates/` candidate lists

## Notes on legacy outputs

Some older chord plots and contingency correlation heatmaps are kept for history. They are labeled as legacy in the plot tables.

If you want a smaller dataset or a pruned output set, define the keep list and I can clean further.
