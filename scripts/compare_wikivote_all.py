import csv
import statistics
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "results" / "raw"
PROCESSED_DIR = BASE_DIR / "results" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


DATABASES = {
    "CognoDB": "cognodb_wikivote_benchmark.csv",
    "Neo4j": "neo4j_wikivote_benchmark.csv",
    "Memgraph": "memgraph_wikivote_benchmark.csv",
    "FalkorDB": "falkordb_wikivote_benchmark.csv",
}


def load_latencies(filename):
    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing benchmark file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = csv.DictReader(file)

        latencies = [
            float(row["latency_ms"])
            for row in rows
            if row["status"] == "success"
            and row["latency_ms"] != ""
        ]

    return latencies


def calculate_metrics(latencies):

    sorted_values = sorted(latencies)

    p95_index = int(
        0.95 * (len(sorted_values) - 1)
    )

    return {
        "measurements": len(latencies),
        "average": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "minimum": min(latencies),
        "maximum": max(latencies),
        "p95": sorted_values[p95_index],
    }


def main():

    print("=" * 78)
    print(
        "CognoDB vs Neo4j vs Memgraph vs FalkorDB "
        "- Wiki-Vote Benchmark"
    )
    print("=" * 78)

    results = {}

    for database, filename in DATABASES.items():

        latencies = load_latencies(filename)

        results[database] = calculate_metrics(
            latencies
        )

    print()
    print(
        f"{'Metric':<32}"
        f"{'CognoDB':>14}"
        f"{'Neo4j':>14}"
        f"{'Memgraph':>14}"
        f"{'FalkorDB':>14}"
    )

    print("-" * 88)

    metrics = [
        ("Measurements", "measurements"),
        ("Average latency (ms)", "average"),
        ("Median / P50 (ms)", "median"),
        ("Minimum latency (ms)", "minimum"),
        ("Maximum latency (ms)", "maximum"),
        ("P95 latency (ms)", "p95"),
    ]

    for label, key in metrics:

        values = [
            results["CognoDB"][key],
            results["Neo4j"][key],
            results["Memgraph"][key],
            results["FalkorDB"][key],
        ]

        if key == "measurements":

            print(
                f"{label:<32}"
                f"{values[0]:>14}"
                f"{values[1]:>14}"
                f"{values[2]:>14}"
                f"{values[3]:>14}"
            )

        else:

            print(
                f"{label:<32}"
                f"{values[0]:>14.3f}"
                f"{values[1]:>14.3f}"
                f"{values[2]:>14.3f}"
                f"{values[3]:>14.3f}"
            )

    fastest = min(
        results,
        key=lambda db: results[db]["average"],
    )

    print()
    print(
        f"Fastest average latency: {fastest}"
    )

    print()
    print("=" * 78)

    output_file = (
        PROCESSED_DIR
        / "cognodb_vs_neo4j_memgraph_falkordb_wikivote.csv"
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "database",
            "measurements",
            "average_latency_ms",
            "median_p50_ms",
            "minimum_latency_ms",
            "maximum_latency_ms",
            "p95_latency_ms",
        ])

        for database, metrics_data in results.items():

            writer.writerow([
                database,
                metrics_data["measurements"],
                round(
                    metrics_data["average"],
                    3,
                ),
                round(
                    metrics_data["median"],
                    3,
                ),
                round(
                    metrics_data["minimum"],
                    3,
                ),
                round(
                    metrics_data["maximum"],
                    3,
                ),
                round(
                    metrics_data["p95"],
                    3,
                ),
            ])

    print()
    print("Comparison saved")
    print("=" * 78)
    print(output_file)


if __name__ == "__main__":
    main()