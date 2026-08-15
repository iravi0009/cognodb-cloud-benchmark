import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
PROCESSED_DIR = RESULTS_DIR / "processed"
CHARTS_DIR = RESULTS_DIR / "charts"

INPUT_FILE = PROCESSED_DIR / "cognodb_vs_neo4j_wikivote.csv"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def load_results():
    rows = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


def create_average_latency_chart(rows):

    workloads = [
        row["workload"]
        for row in rows
    ]

    cognodb = [
        float(row["cognodb_average_ms"])
        for row in rows
    ]

    neo4j = [
        float(row["neo4j_average_ms"])
        for row in rows
    ]

    x = range(len(workloads))

    width = 0.35

    plt.figure(figsize=(12, 7))

    plt.bar(
        [i - width / 2 for i in x],
        cognodb,
        width,
        label="CognoDB"
    )

    plt.bar(
        [i + width / 2 for i in x],
        neo4j,
        width,
        label="Neo4j"
    )

    plt.xticks(
        list(x),
        workloads,
        rotation=45,
        ha="right"
    )

    plt.ylabel("Average Latency (ms)")
    plt.xlabel("Workload")
    plt.title("Wiki-Vote Average Latency: CognoDB vs Neo4j")

    plt.legend()

    plt.tight_layout()

    output = CHARTS_DIR / "wikivote_average_latency.png"

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {output}")


def create_difference_chart(rows):

    workloads = [
        row["workload"]
        for row in rows
    ]

    differences = [
        float(row["difference_percent"])
        for row in rows
    ]

    plt.figure(figsize=(12, 7))

    plt.bar(
        workloads,
        differences
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.ylabel("Latency Difference (%)")
    plt.xlabel("Workload")
    plt.title("Wiki-Vote Latency Difference by Workload")

    plt.axhline(
        0,
        linewidth=1
    )

    plt.tight_layout()

    output = CHARTS_DIR / "wikivote_latency_difference.png"

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {output}")


def main():

    print("=" * 60)
    print("Wiki-Vote Benchmark Charts")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Comparison file not found: {INPUT_FILE}"
        )

    rows = load_results()

    print(f"Workloads: {len(rows)}")

    create_average_latency_chart(rows)

    create_difference_chart(rows)

    print()
    print("=" * 60)
    print("Charts generated successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()