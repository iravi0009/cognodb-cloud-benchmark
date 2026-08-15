import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "results" / "raw"
CHART_DIR = BASE_DIR / "results" / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)


def load_average(filename):
    path = RAW_DIR / filename

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    values = [
        float(row["latency_ms"])
        for row in rows
        if row["status"] == "success"
    ]

    return sum(values) / len(values)


def main():

    databases = ["CognoDB", "Neo4j", "Memgraph"]

    files = {
        "CognoDB": "cognodb_wikivote_benchmark.csv",
        "Neo4j": "neo4j_wikivote_benchmark.csv",
        "Memgraph": "memgraph_wikivote_benchmark.csv",
    }

    averages = [
        load_average(files[database])
        for database in databases
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(databases, averages)

    plt.title("Wiki-Vote Average Query Latency")
    plt.ylabel("Average Latency (ms)")
    plt.xlabel("Database")

    output = CHART_DIR / "wikivote_all_database_latency.png"

    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()

    print(f"Created: {output}")


if __name__ == "__main__":
    main()