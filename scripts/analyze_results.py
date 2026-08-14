import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "results" / "raw" / "cognodb_benchmark.csv"

PROCESSED_DIR = BASE_DIR / "results" / "processed"
CHARTS_DIR = BASE_DIR / "results" / "charts"


# =========================================================
# Setup
# =========================================================

def setup_directories():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Load data
# =========================================================

def load_data():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Benchmark result file not found:\n{RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    if df.empty:
        raise ValueError("Benchmark CSV is empty.")

    required_columns = {
        "timestamp_utc",
        "database",
        "workload",
        "description",
        "run",
        "status",
        "latency_ms",
        "record_count",
        "error",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    return df


# =========================================================
# Clean data
# =========================================================

def clean_data(df):
    df = df.copy()

    df["latency_ms"] = pd.to_numeric(
        df["latency_ms"],
        errors="coerce",
    )

    df["record_count"] = pd.to_numeric(
        df["record_count"],
        errors="coerce",
    )

    df["run"] = pd.to_numeric(
        df["run"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "workload",
            "latency_ms",
        ]
    )

    return df


# =========================================================
# Workload statistics
# =========================================================

def calculate_workload_summary(df):

    summary = (
        df.groupby(
            [
                "database",
                "workload",
                "description",
            ],
            as_index=False,
        )
        .agg(
            measurements=("latency_ms", "count"),
            average_latency_ms=("latency_ms", "mean"),
            median_latency_ms=("latency_ms", "median"),
            minimum_latency_ms=("latency_ms", "min"),
            maximum_latency_ms=("latency_ms", "max"),
            p95_latency_ms=(
                "latency_ms",
                lambda x: x.quantile(0.95),
            ),
            average_record_count=(
                "record_count",
                "mean",
            ),
        )
    )

    summary["success_rate_percent"] = (
        df.groupby(
            [
                "database",
                "workload",
                "description",
            ]
        )["status"]
        .apply(
            lambda x: (
                x.astype(str)
                .str.lower()
                .eq("success")
                .mean()
                * 100
            )
        )
        .values
    )

    summary = summary.sort_values(
        "average_latency_ms"
    )

    return summary


# =========================================================
# Overall statistics
# =========================================================

def calculate_overall_summary(df):

    total = len(df)

    successful = (
        df["status"]
        .astype(str)
        .str.lower()
        .eq("success")
        .sum()
    )

    errors = total - successful

    latency = df["latency_ms"]

    result = pd.DataFrame(
        [
            {
                "database": (
                    df["database"].iloc[0]
                    if "database" in df.columns
                    else "unknown"
                ),
                "total_measurements": total,
                "successful_measurements": successful,
                "error_measurements": errors,
                "success_rate_percent": (
                    successful / total * 100
                    if total
                    else 0
                ),
                "average_latency_ms": latency.mean(),
                "median_latency_ms": latency.median(),
                "minimum_latency_ms": latency.min(),
                "maximum_latency_ms": latency.max(),
                "p95_latency_ms": latency.quantile(0.95),
                "p99_latency_ms": latency.quantile(0.99),
            }
        ]
    )

    return result


# =========================================================
# Chart 1 — Average latency by workload
# =========================================================

def create_latency_by_workload_chart(summary):

    plot_data = summary.sort_values(
        "average_latency_ms"
    )

    plt.figure(figsize=(12, 7))

    plt.bar(
        plot_data["workload"],
        plot_data["average_latency_ms"],
    )

    plt.title(
        "CognoDB Average Latency by Workload"
    )

    plt.xlabel("Workload")
    plt.ylabel("Average Latency (ms)")

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output = (
        CHARTS_DIR
        / "latency_by_workload.png"
    )

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    return output


# =========================================================
# Chart 2 — Latency distribution
# =========================================================

def create_latency_distribution_chart(df):

    plt.figure(figsize=(10, 6))

    plt.hist(
        df["latency_ms"],
        bins=15,
    )

    plt.title(
        "CognoDB Benchmark Latency Distribution"
    )

    plt.xlabel("Latency (ms)")
    plt.ylabel("Number of Measurements")

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output = (
        CHARTS_DIR
        / "latency_distribution.png"
    )

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    return output


# =========================================================
# Chart 3 — Min / Average / P95 / Max
# =========================================================

def create_workload_comparison_chart(summary):

    plot_data = summary.sort_values(
        "average_latency_ms"
    )

    x = range(len(plot_data))

    plt.figure(figsize=(13, 7))

    plt.plot(
        x,
        plot_data["minimum_latency_ms"],
        marker="o",
        label="Minimum",
    )

    plt.plot(
        x,
        plot_data["average_latency_ms"],
        marker="o",
        label="Average",
    )

    plt.plot(
        x,
        plot_data["p95_latency_ms"],
        marker="o",
        label="P95",
    )

    plt.plot(
        x,
        plot_data["maximum_latency_ms"],
        marker="o",
        label="Maximum",
    )

    plt.title(
        "CognoDB Workload Latency Comparison"
    )

    plt.xlabel("Workload")
    plt.ylabel("Latency (ms)")

    plt.xticks(
        list(x),
        plot_data["workload"],
        rotation=45,
        ha="right",
    )

    plt.legend()

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output = (
        CHARTS_DIR
        / "workload_comparison.png"
    )

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    return output


# =========================================================
# Console report
# =========================================================

def print_report(
    df,
    workload_summary,
    overall_summary,
):

    overall = overall_summary.iloc[0]

    print()
    print("=" * 60)
    print("CognoDB Benchmark Analysis")
    print("=" * 60)

    print()
    print("Overall Results")
    print("-" * 40)

    print(
        f"Total measurements : "
        f"{int(overall['total_measurements']):,}"
    )

    print(
        f"Successful         : "
        f"{int(overall['successful_measurements']):,}"
    )

    print(
        f"Errors             : "
        f"{int(overall['error_measurements']):,}"
    )

    print(
        f"Success rate       : "
        f"{overall['success_rate_percent']:.2f}%"
    )

    print(
        f"Average latency    : "
        f"{overall['average_latency_ms']:.3f} ms"
    )

    print(
        f"Median latency     : "
        f"{overall['median_latency_ms']:.3f} ms"
    )

    print(
        f"Minimum latency    : "
        f"{overall['minimum_latency_ms']:.3f} ms"
    )

    print(
        f"Maximum latency    : "
        f"{overall['maximum_latency_ms']:.3f} ms"
    )

    print(
        f"P95 latency        : "
        f"{overall['p95_latency_ms']:.3f} ms"
    )

    print(
        f"P99 latency        : "
        f"{overall['p99_latency_ms']:.3f} ms"
    )

    print()
    print("Workload Summary")
    print("-" * 60)

    for _, row in workload_summary.iterrows():

        print(
            f"{row['workload']:<28} "
            f"avg={row['average_latency_ms']:.3f} ms  "
            f"p95={row['p95_latency_ms']:.3f} ms"
        )

    fastest = workload_summary.iloc[0]

    slowest = workload_summary.iloc[-1]

    print()
    print("Fastest workload:")
    print(
        f"  {fastest['workload']} "
        f"({fastest['average_latency_ms']:.3f} ms)"
    )

    print()
    print("Slowest workload:")
    print(
        f"  {slowest['workload']} "
        f"({slowest['average_latency_ms']:.3f} ms)"
    )


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 60)
    print("CognoDB Benchmark Result Analyzer")
    print("=" * 60)

    print()
    print(f"Input file: {RAW_FILE}")

    setup_directories()

    print()
    print("Loading benchmark results...")

    df = load_data()

    print(
        f"Loaded {len(df):,} measurements."
    )

    df = clean_data(df)

    print(
        f"Valid measurements: {len(df):,}"
    )

    print()
    print("Calculating workload statistics...")

    workload_summary = calculate_workload_summary(
        df
    )

    print(
        f"Analyzed "
        f"{len(workload_summary):,} workloads."
    )

    print()
    print("Calculating overall statistics...")

    overall_summary = calculate_overall_summary(
        df
    )

    # -----------------------------------------------------
    # Save processed CSV files
    # -----------------------------------------------------

    summary_file = (
        PROCESSED_DIR
        / "cognodb_summary.csv"
    )

    overall_file = (
        PROCESSED_DIR
        / "cognodb_overall.csv"
    )

    workload_summary.to_csv(
        summary_file,
        index=False,
    )

    overall_summary.to_csv(
        overall_file,
        index=False,
    )

    print()
    print("Processed results saved:")
    print(f"  {summary_file}")
    print(f"  {overall_file}")

    # -----------------------------------------------------
    # Generate charts
    # -----------------------------------------------------

    print()
    print("Generating charts...")

    chart1 = create_latency_by_workload_chart(
        workload_summary
    )

    chart2 = create_latency_distribution_chart(
        df
    )

    chart3 = create_workload_comparison_chart(
        workload_summary
    )

    print()
    print("Charts saved:")
    print(f"  {chart1}")
    print(f"  {chart2}")
    print(f"  {chart3}")

    # -----------------------------------------------------
    # Print final report
    # -----------------------------------------------------

    print_report(
        df,
        workload_summary,
        overall_summary,
    )

    print()
    print("=" * 60)
    print("Analysis completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:

        print()
        print("=" * 60)
        print("Analysis failed")
        print("=" * 60)

        print(
            f"{type(exc).__name__}: {exc}"
        )

        sys.exit(1)