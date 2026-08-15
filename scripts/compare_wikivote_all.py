import csv
from pathlib import Path
from statistics import mean, median

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS = BASE_DIR / "results" / "raw"


def load_results(filename):
    path = RESULTS / filename

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    return [
        float(row["latency_ms"])
        for row in rows
        if row["status"] == "success"
    ]


def stats(values):
    values = sorted(values)
    p95 = values[int(0.95 * (len(values) - 1))]

    return {
        "count": len(values),
        "average": mean(values),
        "median": median(values),
        "minimum": min(values),
        "maximum": max(values),
        "p95": p95,
    }


def main():

    databases = {
        "CognoDB": "cognodb_wikivote_benchmark.csv",
        "Neo4j": "neo4j_wikivote_benchmark.csv",
        "Memgraph": "memgraph_wikivote_benchmark.csv",
    }

    results = {}

    for database, filename in databases.items():
        results[database] = stats(load_results(filename))

    print("=" * 70)
    print("CognoDB vs Neo4j vs Memgraph - Wiki-Vote Benchmark")
    print("=" * 70)

    print()
    print(
        f"{'Metric':<25}"
        f"{'CognoDB':>15}"
        f"{'Neo4j':>15}"
        f"{'Memgraph':>15}"
    )

    print("-" * 70)

    for metric, label in [
        ("count", "Measurements"),
        ("average", "Average latency (ms)"),
        ("median", "Median / P50 (ms)"),
        ("minimum", "Minimum latency (ms)"),
        ("maximum", "Maximum latency (ms)"),
        ("p95", "P95 latency (ms)"),
    ]:

        print(
            f"{label:<25}"
            f"{results['CognoDB'][metric]:>15.3f}"
            f"{results['Neo4j'][metric]:>15.3f}"
            f"{results['Memgraph'][metric]:>15.3f}"
        )

    fastest = min(
        results,
        key=lambda db: results[db]["average"]
    )

    print()
    print(f"Fastest average latency: {fastest}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()