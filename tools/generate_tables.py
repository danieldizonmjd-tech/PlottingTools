#!/usr/bin/env python3
"""Generate table PNGs summarizing plots and README content."""
from pathlib import Path
import argparse
import textwrap
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / 'plotting_tool_graphs'

CORE_FILES = {
    'correlation_heatmap_variability_metrics.png',
    'heatmap_yso_vs_variability_row_norm.png',
    'heatmap_lc_vs_variability_row_norm.png',
    'pearson_residuals_yso_vs_variability.png',
    'pearson_residuals_lc_vs_variability.png',
    'pearson_residuals_yso_vs_lc.png',
    'scatter_dispersion_vs_median_mag.png',
    'scatter_dispersion_over_error_vs_median_mag.png',
    'statistical_summary.png',
}

META = {
    'correlation_heatmap_variability_metrics.png': (
        'generate_improved_visualizations.py', '318-328',
        'Numeric metric correlation heatmap', 'Core metric-coupling diagnostic'
    ),
    'heatmap_yso_vs_variability_row_norm.png': (
        'generate_improved_visualizations.py', '330-340',
        'YSO class vs variability row percent', 'Class comparison without count bias'
    ),
    'heatmap_lc_vs_variability_row_norm.png': (
        'generate_improved_visualizations.py', '342-352',
        'LCType vs variability row percent', 'Morphology-to-amplitude comparison'
    ),
    'pearson_residuals_yso_vs_variability.png': (
        'generate_improved_visualizations.py', '354-365',
        'Residual heatmap YSO class x variability', 'Over and under represented cells'
    ),
    'pearson_residuals_lc_vs_variability.png': (
        'generate_improved_visualizations.py', '367-378',
        'Residual heatmap LCType x variability', 'Cell-level enrichment by morphology'
    ),
    'pearson_residuals_yso_vs_lc.png': (
        'generate_improved_visualizations.py', '380-391',
        'Residual heatmap YSO class x LCType', 'Class-type pairing signal'
    ),
    'heatmap_irregular_subtypes_row_norm.png': (
        'generate_improved_visualizations.py', '393-406',
        'Irregular subtype row percent by class', 'Extinction-like vs accretion-like split'
    ),
    'scatter_color_slope_vs_variability.png': (
        'generate_improved_visualizations.py', '408-422',
        'Color slope vs amplitude scatter', 'Physical driver clues from color behavior'
    ),
    'scatter_dispersion_vs_median_mag.png': (
        'generate_dispersion_vs_median_plots.py', '81-92',
        'sig_W2Flux vs W2magMed scatter', 'Brightness-dependent scatter check'
    ),
    'scatter_dispersion_over_error_vs_median_mag.png': (
        'generate_dispersion_vs_median_plots.py', '94-102',
        'sig_W2Flux/err_W2Flux vs W2magMed', 'Noise-normalized variability significance'
    ),
    'heatmap_yso_var_row_norm.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '494-500',
        'Alias of YSO vs variability row percent', 'Duplicate naming family'
    ),
    'heatmap_lc_var_row_norm.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '501-507',
        'Alias of LCType vs variability row percent', 'Duplicate naming family'
    ),
    'heatmap_yso_lc_row_norm.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '508-514',
        'YSO class vs LCType row percent', 'Composition view of class-type links'
    ),
    'pearson_residuals_yso_var.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '517-523',
        'Alias residuals YSO class x variability', 'Duplicate naming family'
    ),
    'pearson_residuals_lc_var.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '524-530',
        'Alias residuals LCType x variability', 'Duplicate naming family'
    ),
    'pearson_residuals_yso_lc.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '531-537',
        'Alias residuals YSO class x LCType', 'Duplicate naming family'
    ),
    'statistical_summary.png': (
        'archive/extra_analysis/generate_comprehensive_visualizations.py', '538-566',
        '4-panel statistical summary', 'Compact chi2, effect size, imbalance report'
    ),
    'chord_correlation_metrics.png': (
        'archive/legacy_scripts/generate_fixed_visualizations.py / archive/legacy_scripts/YSO_Chord_Project.ipynb', '177-194 / 271',
        'Legacy chord-style metric relationship view', 'Historical presentation figure'
    ),
    'chord_yso_class_vs_lightcurve.png': (
        'archive/legacy_scripts/YSO_Chord_Project.ipynb', '360',
        'Legacy chord class vs LCType', 'Historical presentation figure'
    ),
    'chord_yso_class_vs_variability.png': (
        'archive/legacy_scripts/YSO_Chord_Project.ipynb', '411',
        'Legacy chord class vs variability', 'Historical presentation figure'
    ),
    'chord_lightcurve_vs_variability.png': (
        'archive/legacy_scripts/YSO_Chord_Project.ipynb', '462',
        'Legacy chord LCType vs variability', 'Historical presentation figure'
    ),
    'correlation_heatmap_yso_vs_lc.png': (
        'archive/legacy_scripts/generate_fixed_visualizations.py', '262-282',
        'Legacy contingency-correlation heatmap', 'Distribution similarity, not primary effect size'
    ),
    'correlation_heatmap_yso_vs_variability.png': (
        'archive/legacy_scripts/generate_fixed_visualizations.py', '286-306',
        'Legacy contingency-correlation heatmap', 'Distribution similarity, not primary effect size'
    ),
    'correlation_heatmap_lc_vs_variability.png': (
        'archive/legacy_scripts/generate_fixed_visualizations.py', '310-330',
        'Legacy contingency-correlation heatmap', 'Distribution similarity, not primary effect size'
    ),
    'cramers_v_yso_variability.png': (
        'No active generator found', 'n/a',
        'Historical effect-size output', 'Archive unless generator is restored'
    ),
    'heatmap_yso_var_contingency.png': (
        'No active generator found', 'n/a',
        'Historical contingency heatmap', 'Archive unless generator is restored'
    ),
    'heatmap_lc_var_contingency.png': (
        'No active generator found', 'n/a',
        'Historical contingency heatmap', 'Archive unless generator is restored'
    ),
    'heatmap_yso_lc_contingency.png': (
        'No active generator found', 'n/a',
        'Historical contingency heatmap', 'Archive unless generator is restored'
    ),
}


def family_for(name: str) -> str:
    if name in CORE_FILES:
        return 'primary'
    if name.startswith('chord_') or 'contingency' in name or (name.startswith('correlation_heatmap_') and name != 'correlation_heatmap_variability_metrics.png') or name.startswith('cramers_v_'):
        return 'archive'
    return 'supplement'


def render_table(headers, rows, out_path, title):
    wrap = [42, 10, 34, 12, 35, 45]
    cell_text = []
    for r in rows:
        cell_text.append([
            textwrap.fill(r[0], wrap[0]),
            textwrap.fill(r[1], wrap[1]),
            textwrap.fill(r[2], wrap[2]),
            textwrap.fill(r[3], wrap[3]),
            textwrap.fill(r[4], wrap[4]),
            textwrap.fill(r[5], wrap[5]),
        ])

    fig_h = 0.9 * (len(rows) + 2)
    fig, ax = plt.subplots(figsize=(26, fig_h))
    ax.axis('off')

    col_widths = [0.24, 0.08, 0.20, 0.07, 0.20, 0.21]
    table = ax.table(
        cellText=cell_text,
        colLabels=headers,
        colWidths=col_widths,
        cellLoc='left',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 2.0)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor('#1f3a5f')
            cell.set_text_props(weight='bold', color='white')
        else:
            cell.set_facecolor('#f7fafc' if r % 2 else '#e8f0f6')
        cell.set_edgecolor('#708090')

    ax.set_title(title, fontsize=15, fontweight='bold', pad=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close()


def generate_all_graphs_table():
    files = sorted(
        p for p in PLOTS.rglob('*.png')
        if not p.name.startswith('readme_plot_table')
        and not p.name.startswith('all_graphs_table')
    )
    rows = []
    for p in files:
        rel = p.relative_to(PLOTS).as_posix()
        name = p.name
        script, lines, role, meaning = META.get(name, ('Unknown', 'n/a', 'Unmapped plot', 'Needs manual classification'))
        rows.append((rel, family_for(name), script, lines, role, meaning))

    headers = ['PNG Path', 'Family', 'Generated By', 'Line Ref', 'Function', 'Meaning']
    rows_per_page = 12
    pages = [rows[i:i + rows_per_page] for i in range(0, len(rows), rows_per_page)]

    for idx, page in enumerate(pages, start=1):
        out = PLOTS / f'all_graphs_table_p{idx}.png'
        render_table(headers, page, out, f'All plotting_tool_graphs PNG Inventory (Page {idx}/{len(pages)})')


def generate_readme_summary_table():
    rows = [
        (
            'correlation_heatmap_variability_metrics.png',
            'Numeric metric correlation heatmap',
            'generate_improved_visualizations.py:318-328',
            'Keep',
            'Checks metric coupling; delW2mag and sig_W2Flux track variability physics.'
        ),
        (
            'heatmap_yso_vs_variability_row_norm.png',
            'YSO class vs variability row percent',
            'generate_improved_visualizations.py:330-340',
            'Keep',
            'Compares variability distribution per class without count bias.'
        ),
        (
            'heatmap_lc_vs_variability_row_norm.png',
            'LCType vs variability row percent',
            'generate_improved_visualizations.py:342-352',
            'Keep',
            'Morphology links strongly to amplitude regime.'
        ),
        (
            'pearson_residuals_yso_vs_variability.png',
            'Residuals YSO class x variability',
            'generate_improved_visualizations.py:354-365',
            'Keep',
            'Highlights cells above or below expectation.'
        ),
        (
            'pearson_residuals_lc_vs_variability.png',
            'Residuals LCType x variability',
            'generate_improved_visualizations.py:367-378',
            'Keep',
            'Identifies enriched morphologies by variability.'
        ),
        (
            'pearson_residuals_yso_vs_lc.png',
            'Residuals YSO class x LCType',
            'generate_improved_visualizations.py:380-391',
            'Keep',
            'Tests class-type pairing patterns.'
        ),
        (
            'scatter_dispersion_vs_median_mag.png',
            'sig_W2Flux vs W2magMed scatter',
            'generate_dispersion_vs_median_plots.py:81-92',
            'Keep',
            'Checks scatter versus brightness.'
        ),
        (
            'scatter_dispersion_over_error_vs_median_mag.png',
            'sig_W2Flux/err_W2Flux vs W2magMed',
            'generate_dispersion_vs_median_plots.py:94-102',
            'Keep',
            'Noise-normalized variability diagnostic.'
        ),
    ]

    headers = ['PNG', 'Function', 'Code Location', 'Keep', 'Meaning']
    wrap = [34, 36, 35, 8, 52]
    wrapped = []
    for r in rows:
        wrapped.append([
            textwrap.fill(r[0], wrap[0]),
            textwrap.fill(r[1], wrap[1]),
            textwrap.fill(r[2], wrap[2]),
            textwrap.fill(r[3], wrap[3]),
            textwrap.fill(r[4], wrap[4]),
        ])

    fig_h = 0.75 * (len(rows) + 2)
    fig, ax = plt.subplots(figsize=(24, fig_h))
    ax.axis('off')

    col_widths = [0.20, 0.19, 0.20, 0.07, 0.34]
    table = ax.table(
        cellText=wrapped,
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
    out = PLOTS / 'readme_plot_table.png'
    plt.savefig(out, dpi=220, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generate plot summary table PNGs.')
    parser.add_argument('--all', action='store_true', help='Generate all-graphs inventory tables')
    parser.add_argument('--readme', action='store_true', help='Generate README summary table')
    args = parser.parse_args()

    if not args.all and not args.readme:
        args.all = True
        args.readme = True

    if args.readme:
        generate_readme_summary_table()
    if args.all:
        generate_all_graphs_table()


if __name__ == '__main__':
    main()
