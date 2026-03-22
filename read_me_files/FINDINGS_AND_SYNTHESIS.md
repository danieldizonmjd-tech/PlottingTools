# Findings & Synthesis (Physics‑first, Human‑readable)

This update replaces raw‑count chord plots with normalized distributions, Pearson residuals, and color‑slope physics. The goal is to highlight *which behaviors are genuinely enriched* in specific classes or light‑curve types, not just which categories are large.

## What Changed (and Why)
- **Normalized contingency tables** expose proportional behavior instead of Class II dominance by raw counts.
- **Pearson residual heatmaps** show statistically meaningful deviations from random expectation.
- **Color‑slope analysis** (W1–W2 vs W2) splits “Irregular” into extinction‑like vs accretion‑like behavior.

## Key Quantitative Results (QC: Number ≥ 10)

### 1) Class Imbalance (still real, now handled)
- **Class II** = 61.1% of the sample.
- **LCType NV** = 73.8% (extreme imbalance).
- This is why normalization and residuals are essential.

### 2) YSO Class vs Variability (Row‑normalized %)
- **Class I**: High 27.5%, Low 32.7%, Medium 39.7%
- **Class II**: High 21.4%, Low 21.8%, Medium 56.8%
- **Class III**: High 23.0%, Low 34.2%, Medium 42.8%
- **Flat Spectrum**: High 29.7%, Low 17.9%, Medium 52.4%

Interpretation:
- **Class II is not “more variable”** once normalized; it’s just more common.
- **Flat‑Spectrum sources have the highest High‑variability fraction** (29.7%), suggesting elevated episodic behavior in transitional objects.
- **Class I and Class III are enriched in Low variability** relative to expectation (see residuals below).

### 3) LCType vs Variability (Row‑normalized %)
- **Irregular**: High 65.1%, Medium 34.8%, Low ~0%
- **Burst**: High 61.7%
- **Drop**: High 55.7%
- **Periodic**: High 51.1%
- **NV**: High 10.8%, Low 30.7%, Medium 58.5%

Interpretation:
- **LCType is the dominant predictor of amplitude category**, not class. This is quantified by Cramér’s V:
  - YSO Class ↔ Variability: **V = 0.108 (weak)**
  - LCType ↔ Variability: **V = 0.385 (moderate)**
  - YSO Class ↔ LCType: **V = 0.088 (negligible)**

### 4) Pearson Residuals (where the surprises are)
**YSO Class vs Variability** (largest deviations):
- **Class III × Low**: +9.20 (over‑represented)
- **Class I × Low**: +8.96 (over‑represented)
- **Class I × Medium**: −8.34 (under‑represented)
- **FS × High**: +7.86 (over‑represented)
- **FS × Low**: −7.07 (under‑represented)
- **Class II × Medium**: +5.90 (over‑represented)

**YSO Class vs LCType** (largest deviations):
- **FS × Irregular**: +14.25 (strong enrichment)
- **FS × NV**: −8.08 (strong deficit)
- **Class II × Irregular**: −7.09 (deficit)
- **Class I × Curved**: +7.05 (enrichment)
- **Class I × Linear**: +6.33 (enrichment)

**LCType vs Variability** (largest deviations):
- **Irregular × High**: +54.6 (dominant signal)
- **NV × High**: −33.0 (strong deficit)
- **Irregular × Low**: −30.9 (strong deficit)

Interpretation:
- **Flat‑Spectrum objects are disproportionately Irregular**, which fits a transitional, unstable phase.
- **Class I enriches linear/curved trends**, suggesting monotonic accretion or extinction events.
- **Irregular essentially *means* High variability** in this dataset.

### 5) “Irregular” Deconstructed Using Color Slope
We split Irregular light curves using `slope_color` (W1–W2 vs W2):
- **Positive slope** → redder when fainter (extinction‑like “Faders”)
- **Negative slope** → bluer when brighter (accretion‑like)

Row‑normalized split by class:
- **Class I**: 28.8% Accretor‑like, 25.8% Fader‑like, 45.3% Stochastic
- **Class II**: 38.8% Accretor‑like, 10.3% Fader‑like, 50.9% Stochastic
- **Class III**: 49.8% Accretor‑like, 6.7% Fader‑like, 43.5% Stochastic
- **FS**: 24.6% Accretor‑like, 21.7% Fader‑like, 53.8% Stochastic

Interpretation:
- **Class III irregulars skew accretion‑like**, not extinction‑like, consistent with chromospheric or hot‑spot variability.
- **Class I shows the strongest extinction‑like fraction**, consistent with embedded dust.
- **Class II irregulars are mostly stochastic with a smaller extinction component.**

### 6) Color‑Slope vs Amplitude (Physical Check)
- **Correlation: `slope_color` ↔ `delW2mag` = 0.049** (very weak)
- This suggests **color evolution is not simply amplitude‑driven**; it depends on the physical mechanism (dust vs accretion), not just variability size.

### 7) Metric Correlation Caveat
- `sig_W2Flux` ↔ `delW2mag` shows **r = 0.436**, which is largely **mathematical coupling** (both measure variance). We keep it but treat it as expected, not physical insight.

## Bottom Line (Astrophysical Takeaway)
- **Light‑curve morphology is the most meaningful axis** for understanding variability amplitude.
- **Class alone is a weak predictor** once normalized.
- **Color slope adds physical meaning**: it separates extinction‑driven faders from accretion‑driven brightenings within the Irregular bin.
- The pipeline now surfaces *surprises*, not just big counts.

## Where to Look
- Normalized distributions: `plotting_tool_graphs/heatmap_*_row_norm.png`
- Residuals: `plotting_tool_graphs/pearson_residuals_*.png`
- Physics overlay: `plotting_tool_graphs/scatter_color_slope_vs_variability.png`
- Irregular subtypes: `plotting_tool_graphs/heatmap_irregular_subtypes_row_norm.png`
