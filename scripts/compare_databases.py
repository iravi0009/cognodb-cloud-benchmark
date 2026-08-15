import csv
from pathlib import Path
from statistics import mean, median


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "results" / "raw"
PROCESSED_DIR = BASE_DIR / "results" / "processed"
CHARTS_DIR = BASE_DIR / "results" / "charts"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


COGNODB_FILE = RAW_DIR / "cognodb_benchmark.csv"
NEO4J_FILE = RAW_DIR / "neo4j_benchmark.csv"

OUTPUT_FILE = (
    PROCESSED_DIR / "cognodb_vs_neo4j.csv"
)


# ---------------------------------------------------------
# Load CSV
# ---------------------------------------------------------

def load_results(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing benchmark file: {path}"
        )

    rows = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["status"] != "success":
                continue

            rows.append(
                {
                    "database": row["database"],
                    "workload": row["workload"],
                    "description": row["description"],
                    "run": int(row["run"]),
                    "latency_ms": float(row["latency_ms"]),
                    "record_count": int(
                        row["record_count"]
                    ),
                }
            )

    return rows


# ---------------------------------------------------------
# Percentile
# ---------------------------------------------------------

def percentile(values, percentile):

    values = sorted(values)

    if not values:
        return 0.0

    index = (
        percentile
        * (len(values) - 1)
    )

    lower = int(index)
    upper = min(
        lower + 1,
        len(values) - 1,
    )

    weight = index - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * weight
    )


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

def calculate_statistics(rows):

    latencies = [
        row["latency_ms"]
        for row in rows
    ]

    return {
        "measurements": len(latencies),
        "average": mean(latencies),
        "median": median(latencies),
        "minimum": min(latencies),
        "maximum": max(latencies),
        "p95": percentile(
            latencies,
            0.95,
        ),
        "success_rate": 100.0,
    }


# ---------------------------------------------------------
# Main comparison
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("CognoDB vs Neo4j Benchmark Comparison")
    print("=" * 70)

    cognodb_rows = load_results(
        COGNODB_FILE
    )

    neo4j_rows = load_results(
        NEO4J_FILE
    )

    print()
    print(
        f"CognoDB measurements: "
        f"{len(cognodb_rows):,}"
    )

    print(
        f"Neo4j measurements: "
        f"{len(neo4j_rows):,}"
    )

    # -----------------------------------------------------
    # Overall statistics
    # -----------------------------------------------------

    cognodb_stats = calculate_statistics(
        cognodb_rows
    )

    neo4j_stats = calculate_statistics(
        neo4j_rows
    )

    print()
    print("=" * 70)
    print("Overall Results")
    print("=" * 70)

    print()
    print(
        f"{'Metric':<25}"
        f"{'CognoDB':>15}"
        f"{'Neo4j':>15}"
    )

    print("-" * 55)

    metrics = [
        (
            "Measurements",
            "measurements",
            ".0f",
        ),
        (
            "Average latency (ms)",
            "average",
            ".3f",
        ),
        (
            "Median latency (ms)",
            "median",
            ".3f",
        ),
        (
            "Minimum latency (ms)",
            "minimum",
            ".3f",
        ),
        (
            "Maximum latency (ms)",
            "maximum",
            ".3f",
        ),
        (
            "P95 latency (ms)",
            "p95",
            ".3f",
        ),
        (
            "Success rate (%)",
            "success_rate",
            ".1f",
        ),
    ]

    for label, key, fmt in metrics:

        cognodb_value = format(
            cognodb_stats[key],
            fmt,
        )

        neo4j_value = format(
            neo4j_stats[key],
            fmt,
        )

        print(
            f"{label:<25}"
            f"{cognodb_value:>15}"
            f"{neo4j_value:>15}"
        )

    # -----------------------------------------------------
    # Overall speed difference
    # -----------------------------------------------------

    average_cognodb = (
        cognodb_stats["average"]
    )

    average_neo4j = (
        neo4j_stats["average"]
    )

    if average_cognodb < average_neo4j:

        improvement = (
            (
                average_neo4j
                - average_cognodb
            )
            / average_neo4j
        ) * 100

        faster = "CognoDB"

    else:

        improvement = (
            (
                average_cognodb
                - average_neo4j
            )
            / average_cognodb
        ) * 100

        faster = "Neo4j"

    print()
    print(
        f"Faster overall database: {faster}"
    )

    print(
        f"Average latency difference: "
        f"{improvement:.2f}%"
    )

    # -----------------------------------------------------
    # Per workload
    # -----------------------------------------------------

    cognodb_workloads = {}

    for row in cognodb_rows:

        cognodb_workloads.setdefault(
            row["workload"],
            [],
        ).append(row["latency_ms"])

    neo4j_workloads = {}

    for row in neo4j_rows:

        neo4j_workloads.setdefault(
            row["workload"],
            [],
        ).append(row["latency_ms"])

    comparison_rows = []

    print()
    print("=" * 70)
    print("Per-Workload Comparison")
    print("=" * 70)

    for workload in cognodb_workloads:

        c_values = cognodb_workloads[
            workload
        ]

        n_values = neo4j_workloads.get(
            workload,
            [],
        )

        if not n_values:
            continue

        c_average = mean(c_values)
        n_average = mean(n_values)

        if c_average < n_average:

            faster_db = "cognodb"

            difference = (
                (
                    n_average
                    - c_average
                )
                / n_average
            ) * 100

        else:

            faster_db = "neo4j"

            difference = (
                (
                    c_average
                    - n_average
                )
                / c_average
            ) * 100

        print()
        print(
            f"Workload: {workload}"
        )

        print(
            f"  CognoDB average: "
            f"{c_average:.3f} ms"
        )

        print(
            f"  Neo4j average:   "
            f"{n_average:.3f} ms"
        )

        print(
            f"  Faster: {faster_db}"
        )

        print(
            f"  Difference: "
            f"{difference:.2f}%"
        )

        comparison_rows.append(
            {
                "workload": workload,
                "cognodb_average_ms":
                    round(c_average, 3),
                "neo4j_average_ms":
                    round(n_average, 3),
                "faster_database":
                    faster_db,
                "difference_percent":
                    round(
                        difference,
                        2,
                    ),
            }
        )

    # -----------------------------------------------------
    # Save comparison CSV
    # -----------------------------------------------------

    fieldnames = [
        "workload",
        "cognodb_average_ms",
        "neo4j_average_ms",
        "faster_database",
        "difference_percent",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            comparison_rows
        )

    print()
    print("=" * 70)
    print("Comparison saved")
    print("=" * 70)

    print(OUTPUT_FILE)

    print()
    print("=" * 70)
    print("Database Comparison Completed")
    print("=" * 70)


if __name__ == "__main__":
    main()