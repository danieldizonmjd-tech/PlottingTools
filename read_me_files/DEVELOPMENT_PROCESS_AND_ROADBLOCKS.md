# Development Process & Roadblocks

## What changed in this iteration
- Replaced chord diagrams with **normalized heatmaps** and **Pearson residuals**.
- Added **color‑slope physics** (`slope_color`) and **Irregular subtyping**.
- Updated parsers to handle “uncertain” class rows and extra color columns.
- Cleaned scripts to use **project‑relative paths** instead of hard‑coded absolute paths.

## Why it mattered
- Raw counts made Class II look “important” everywhere.
- Pearson correlations on categorical tables hid the interesting deviations.
- Color slope provides a physical link: extinction vs accretion.

## Remaining limitations
- No raw time‑series → can’t compute true stochasticity index or flux symmetry yet.
- LCType imbalance is huge (NV dominates), so residuals and normalization are mandatory.

## Next technical upgrades (if desired)
1. Add time‑series stats once light curves are available.
2. Run class‑balanced resampling to quantify robustness of residual peaks.
3. Build a small “interpretation” report that auto‑extracts top residual cells and writes a narrative summary.
