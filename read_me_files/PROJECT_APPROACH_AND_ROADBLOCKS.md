# Project Approach & Roadblocks (Updated)

## Approach (what we actually do now)
1. **Load Paper B** and apply minimal QC (`Number >= 10`, finite core metrics).
2. **Replace raw counts with normalized tables** so Class II dominance doesn’t mask real behavior.
3. **Use Pearson residuals** to highlight cells with more/fewer sources than expected by chance.
4. **Add physics via color slope** (W1–W2 vs W2):
   - Positive slope → redder when fainter → extinction
   - Negative slope → bluer when brighter → accretion
5. **Decompose “Irregular”** into accretor‑like vs fader‑like vs stochastic.

This is all in `generate_improved_visualizations.py` and outputs to `plotting_tool_graphs/`.

## What we stopped doing (and why)
- **Chord diagrams of raw counts**: pretty but misleading under severe class imbalance.
- **Pearson correlations on contingency tables**: not meaningful for categorical counts.

## Roadblocks / Caveats
- **No raw time‑series in this repo** for stochasticity index or flux symmetry. We use color slope as a physics proxy. If time‑series are added later, this should be upgraded.
- **Class imbalance** is extreme (LCType NV ~74%). Always look at normalized or residual plots, never raw counts.
- **Some correlations are tautological** (e.g., `sig_W2Flux` vs `delW2mag`). Treat them as sanity checks, not physical insight.

## If you want to extend this
- Add time‑series statistics (stochasticity, flux symmetry) when light curves are available.
- Use class‑balanced bootstraps to test robustness of residual peaks.
- Compare color‑slope distributions across regions or clusters.
