#!/usr/bin/env python3
from pathlib import Path
import textwrap
import matplotlib.pyplot as plt

OUT = Path('/Users/marcus/Desktop/YSO Plotting Copy/plotting_tool_graphs/readme_plot_table.png')

rows = [
    ("correlation_heatmap_variability_metrics.png",
     "Correlation matrix of numeric variability metrics",
     "generate_improved_visualizations.py:318-328",
     "Keep",
     "Checks metric coupling; delW2mag and sig_W2Flux should track variability physics."),
    ("heatmap_yso_vs_variability_row_norm.png",
     "Row-normalized YSO class vs variability level",
     "generate_improved_visualizations.py:330-340",
     "Keep",
     "Compares variability distribution per class without raw-count bias."),
    ("heatmap_lc_vs_variability_row_norm.png",
     "Row-normalized LCType vs variability level",
     "generate_improved_visualizations.py:342-352",
     "Keep",
     "Shows morphology is linked to variability amplitude regime."),
    ("pearson_residuals_yso_vs_variability.png",
     "Cell-wise over/under representation for YSO class x variability",
     "generate_improved_visualizations.py:354-365",
     "Keep",
     "Highlights class-amplitude combinations above random expectation."),
    ("pearson_residuals_lc_vs_variability.png",
     "Cell-wise over/under representation for LCType x variability",
     "generate_improved_visualizations.py:367-378",
     "Keep",
     "Identifies which morphologies are enriched at high or low variability."),
    ("pearson_residuals_yso_vs_lc.png",
     "Cell-wise over/under representation for YSO class x LCType",
     "generate_improved_visualizations.py:380-391",
     "Keep",
     "Tests whether morphology has evolutionary-class preference."),
    ("heatmap_irregular_subtypes_row_norm.png",
     "Row-normalized irregular subtype composition by YSO class",
     "generate_improved_visualizations.py:393-406",
     "Optional",
     "Separates likely extinction-like versus accretion-like irregular behavior."),
    ("scatter_color_slope_vs_variability.png",
     "slope_color vs delW2mag scatter",
     "generate_improved_visualizations.py:408-422",
     "Optional",
     "Color trend helps distinguish dust extinction from accretion-like variability."),
    ("scatter_dispersion_vs_median_mag.png",
     "sig_W2Flux vs W2magMed scatter",
     "generate_dispersion_vs_median_plots.py:81-92",
     "Keep",
     "Checks brightness dependence of observed scatter and variability."),
    ("scatter_dispersion_over_error_vs_median_mag.png",
     "(sig_W2Flux/err_W2Flux) vs W2magMed scatter",
     "generate_dispersion_vs_median_plots.py:94-102",
     "Keep",
     "Noise-normalized diagnostic for robust variability across magnitude."),
    ("statistical_summary.png",
     "2x2 panel of chi2, Cramer V, phi, imbalance",
     "generate_comprehensive_visualizations.py:538-566",
     "Keep",
     "Single-page quantitative summary with significance and effect sizes."),
]

headers = ["PNG", "Function", "Code Location", "Keep?", "Astrophysical Meaning"]

wrap_widths = [34, 36, 35, 8, 52]
wrapped_rows = []
for row in rows:
    wrapped_rows.append([
        textwrap.fill(row[0], wrap_widths[0]),
        textwrap.fill(row[1], wrap_widths[1]),
        textwrap.fill(row[2], wrap_widths[2]),
        textwrap.fill(row[3], wrap_widths[3]),
        textwrap.fill(row[4], wrap_widths[4]),
    ])

fig_h = 0.75 * (len(rows) + 2)
fig, ax = plt.subplots(figsize=(24, fig_h))
ax.axis('off')

col_widths = [0.20, 0.19, 0.20, 0.07, 0.34]
table = ax.table(
    cellText=wrapped_rows,
    colLabels=headers,
    colWidths=col_widths,
    cellLoc='left',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.0)

for (r, c), cell in table.get_celld().items():
    if r == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#2f4f4f')
    else:
        cell.set_facecolor('#f9fbfc' if r % 2 else '#eef3f7')
    cell.set_edgecolor('#7f8c8d')

plt.title('YSO Plotting README Summary Table', fontsize=16, weight='bold', pad=18)
plt.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=220, bbox_inches='tight')
print(f'Saved {OUT}')
