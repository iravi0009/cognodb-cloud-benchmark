import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "results"
    / "processed"
    / "wikivote_mixed_concurrency.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "results"
    / "charts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "wikivote_mixed_concurrency.png"
)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Concurrency results not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {}

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            database = row["database"]
            concurrency = int(row["concurrency"])
            throughput = float(row["throughput_qps"])

            if database not in data:
                data[database] = {}

            data[database][concurrency] = throughput

    concurrency_levels = [1, 10, 40]

    plt.figure(figsize=(11, 6))

    for database, values in data.items():

        throughput_values = [
            values[level]
            for level in concurrency_levels
        ]

        plt.plot(
            concurrency_levels,
            throughput_values,
            marker="o",
            linewidth=2,
            label=database,
        )

    plt.title(
        "Wiki-Vote Mixed Read/Write Concurrency Benchmark"
    )

    plt.xlabel(
        "Concurrent Clients"
    )

    plt.ylabel(
        "Throughput (queries/sec)"
    )

    plt.xticks(
        concurrency_levels
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

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