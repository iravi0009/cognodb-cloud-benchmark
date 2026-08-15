import csv
from pathlib import Path
from statistics import mean, median


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "results" / "raw"
PROCESSED_DIR = BASE_DIR / "results" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

COGNODB_FILE = RAW_DIR / "cognodb_wikivote_benchmark.csv"
NEO4J_FILE = RAW_DIR / "neo4j_wikivote_benchmark.csv"

OUTPUT_FILE = PROCESSED_DIR / "cognodb_vs_neo4j_wikivote.csv"


def load_results(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    rows = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["status"] == "success":
                rows.append({
                    "workload": row["workload"],
                    "latency_ms": float(row["latency_ms"]),
                    "record_count": int(row["record_count"]),
                })

    return rows


def percentile(values, p):
    values = sorted(values)

    if not values:
        return 0.0

    index = p * (len(values) - 1)
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def statistics(rows):
    values = [r["latency_ms"] for r in rows]

    return {
        "measurements": len(values),
        "average": mean(values),
        "median": median(values),
        "minimum": min(values),
        "maximum": max(values),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
    }


def main():

    print("=" * 70)
    print("CognoDB vs Neo4j - Wiki-Vote Benchmark Comparison")
    print("=" * 70)

    cognodb = load_results(COGNODB_FILE)
    neo4j = load_results(NEO4J_FILE)

    c = statistics(cognodb)
    n = statistics(neo4j)

    print()
    print(f"CognoDB measurements: {c['measurements']}")
    print(f"Neo4j measurements:   {n['measurements']}")

    print()
    print("=" * 70)
    print("Overall Results")
    print("=" * 70)

    print()
    print(f"{'Metric':<25}{'CognoDB':>15}{'Neo4j':>15}")
    print("-" * 55)

    metrics = [
        ("Measurements", "measurements", ".0f"),
        ("Average latency (ms)", "average", ".3f"),
        ("Median / P50 (ms)", "median", ".3f"),
        ("Minimum latency (ms)", "minimum", ".3f"),
        ("Maximum latency (ms)", "maximum", ".3f"),
        ("P95 latency (ms)", "p95", ".3f"),
        ("P99 latency (ms)", "p99", ".3f"),
    ]

    for label, key, fmt in metrics:
        print(
            f"{label:<25}"
            f"{format(c[key], fmt):>15}"
            f"{format(n[key], fmt):>15}"
        )

    average_difference = (
        (c["average"] - n["average"])
        / c["average"]
    ) * 100

    print()
    print(
        f"Neo4j average latency advantage: "
        f"{average_difference:.2f}%"
    )

    p95_difference = (
        (c["p95"] - n["p95"])
        / c["p95"]
    ) * 100

    print(
        f"Neo4j P95 latency advantage: "
        f"{p95_difference:.2f}%"
    )

    # ---------------------------------------------------------
    # Per-workload comparison
    # ---------------------------------------------------------

    c_workloads = {}
    n_workloads = {}

    for row in cognodb:
        c_workloads.setdefault(row["workload"], []).append(
            row["latency_ms"]
        )

    for row in neo4j:
        n_workloads.setdefault(row["workload"], []).append(
            row["latency_ms"]
        )

    print()
    print("=" * 70)
    print("Per-Workload Comparison")
    print("=" * 70)

    comparison_rows = []

    for workload in c_workloads:

        if workload not in n_workloads:
            continue

        c_avg = mean(c_workloads[workload])
        n_avg = mean(n_workloads[workload])

        if c_avg < n_avg:
            faster = "CognoDB"
            difference = ((n_avg - c_avg) / n_avg) * 100
        else:
            faster = "Neo4j"
            difference = ((c_avg - n_avg) / c_avg) * 100

        print()
        print(f"Workload: {workload}")
        print(f"  CognoDB average: {c_avg:.3f} ms")
        print(f"  Neo4j average:   {n_avg:.3f} ms")
        print(f"  Faster:          {faster}")
        print(f"  Difference:      {difference:.2f}%")

        comparison_rows.append({
            "workload": workload,
            "cognodb_average_ms": round(c_avg, 3),
            "neo4j_average_ms": round(n_avg, 3),
            "faster_database": faster,
            "difference_percent": round(difference, 2),
        })

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "workload",
                "cognodb_average_ms",
                "neo4j_average_ms",
                "faster_database",
                "difference_percent",
            ],
        )

        writer.writeheader()
        writer.writerows(comparison_rows)

    print()
    print("=" * 70)
    print("Comparison saved")
    print("=" * 70)
    print(OUTPUT_FILE)

    print()
    print("Wiki-Vote comparison completed.")


if __name__ == "__main__":
    main()