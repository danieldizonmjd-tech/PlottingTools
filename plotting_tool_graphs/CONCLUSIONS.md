# Conclusions From the Graphs

This file summarizes the main conclusions that follow from the plots in `plotting_tool_graphs`.
The wording is intentionally plain so it can be reused in notes or reports.

## Core conclusions

1. Light curve type is the strongest predictor of variability level.
The LCType versus variability heatmaps and residual maps show strong structure. Irregular and eruptive light curves are concentrated in high variability, while NV concentrates in low or medium variability. This means morphology carries a strong signal about amplitude.

2. YSO class matters, but less than morphology.
The YSO class versus variability plots show trends, but the signal is weaker than LCType. Class gives evolutionary context, yet it is not the dominant predictor of variability amplitude.

3. Variability amplitude is tied to flux dispersion, but brightness and noise matter.
The numeric correlation heatmap shows `delW2mag` tracking `sig_W2Flux`. The dispersion versus magnitude plots show that scatter depends on brightness, so noise-normalized views such as dispersion over error are needed for fair comparison.

4. Irregular sources are not one physical group.
The irregular subtype heatmap and the color slope scatter indicate multiple drivers. Redder when fainter behavior is consistent with variable extinction, while blueing with brightening is consistent with accretion or hot spots. This supports splitting irregular into physically meaningful subtypes.

5. Small categories are fragile.
The dataset is strongly imbalanced. Rare classes and rare LC types have low counts, so their specific patterns are less reliable. Broad conclusions should be drawn from well populated classes and types.

## How to use these conclusions

- Use LCType as the primary lens for variability amplitude.
- Use YSO class as a secondary context for evolutionary stage.
- Use color slope and irregular subtypes to separate physical drivers.
- Use noise-normalized variability metrics when comparing across magnitude.

## Notes about interpretation

- Correlation heatmaps of contingency tables show distribution similarity, not direct causal association.
- Residual heatmaps are best for identifying which cells drive the significance.
- Any statement about rare categories should be marked as tentative.
