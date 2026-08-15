import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "results"
    / "processed"
    / "cognodb_vs_neo4j_memgraph_falkordb_arangodb_wikivote.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "results"
    / "charts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "wikivote_all_database_latency.png"
)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Comparison file not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    databases = []
    averages = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            databases.append(
                row["database"]
            )

            averages.append(
                float(
                    row["average_latency_ms"]
                )
            )

    if not databases:
        raise ValueError(
            "No database results found in comparison file."
        )

    plt.figure(
        figsize=(11, 6)
    )

    plt.bar(
        databases,
        averages,
    )

    plt.title(
        "Wiki-Vote Benchmark - Average Latency"
    )

    plt.xlabel(
        "Database"
    )

    plt.ylabel(
        "Average Latency (ms)"
    )

    plt.xticks(
        rotation=15
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FILE,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Created: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()