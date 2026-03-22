from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from yso_utils import parse_mrt_file


def load_clean_data(input_file: Path) -> pd.DataFrame:
    df = parse_mrt_file(str(input_file))
    required = ["W2magMed", "sig_W2Flux", "err_W2Flux"]
    df = df.dropna(subset=required).copy()
    df = df[(df["sig_W2Flux"] > 0) & (df["err_W2Flux"] > 0)]
    df["dispersion_over_error"] = df["sig_W2Flux"] / df["err_W2Flux"]
    return df


def make_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    out_file: Path,
    title: str,
    y_label: str,
    color_by_lctype: bool,
):
    plt.figure(figsize=(9, 6))
    if color_by_lctype and "LCType" in df.columns:
        # Keep legend readable by limiting to most common classes.
        top_lc = df["LCType"].value_counts().head(8).index
        df_plot = df[df["LCType"].isin(top_lc)].copy()
        sns.scatterplot(
            data=df_plot,
            x=x_col,
            y=y_col,
            hue="LCType",
            s=14,
            alpha=0.55,
            linewidth=0,
        )
        plt.legend(title="LCType", fontsize=8, title_fontsize=9, loc="best")
    else:
        sns.scatterplot(data=df, x=x_col, y=y_col, s=10, alpha=0.35, linewidth=0)

    plt.title(title)
    plt.xlabel("Lightcurve Median Magnitude (W2magMed)")
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate dispersion-vs-median diagnostic plots.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(Path(__file__).resolve().parent / "paper_data_files" / "apjsadc397t2_mrt.txt"),
        help="Input MRT file path.",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=str(Path(__file__).resolve().parent / "plotting_tool_graphs"),
        help="Output directory for plots.",
    )
    parser.add_argument(
        "--color-by-lctype",
        action="store_true",
        help="Color points by LCType (top 8 classes only to keep figure readable).",
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_clean_data(Path(args.input))

    p1 = outdir / "scatter_dispersion_vs_median_mag.png"
    p2 = outdir / "scatter_dispersion_over_error_vs_median_mag.png"

    make_scatter(
        df=df,
        x_col="W2magMed",
        y_col="sig_W2Flux",
        out_file=p1,
        title="Lightcurve Dispersion vs Median Magnitude (Full Sample)",
        y_label="Lightcurve Dispersion (sig_W2Flux)",
        color_by_lctype=args.color_by_lctype,
    )

    make_scatter(
        df=df,
        x_col="W2magMed",
        y_col="dispersion_over_error",
        out_file=p2,
        title="Dispersion / Median Error vs Median Magnitude (Full Sample)",
        y_label="sig_W2Flux / err_W2Flux",
        color_by_lctype=args.color_by_lctype,
    )

    print(f"Saved: {p1}")
    print(f"Saved: {p2}")
    print(f"N points plotted: {len(df)}")


if __name__ == "__main__":
    main()
