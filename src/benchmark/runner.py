import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

from .adapters.cognodb import CognoDBAdapter
from .adapters.neo4j import Neo4jAdapter
from .workloads.queries import WORKLOADS as DEFAULT_WORKLOADS
from .workloads.wikivote_queries import WORKLOADS as WIKIVOTE_WORKLOADS


SUPPORTED_DATABASES = [
    "cognodb",
    "neo4j",
    "memgraph",
    "falkordb",
    "arangodb",
]


BASE_DIR = Path(__file__).resolve().parents[2]

RESULTS_DIR = BASE_DIR / "results"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"

RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def create_adapter(database):
    """
    Create the adapter for the selected database.
    """

    if database == "cognodb":
        return CognoDBAdapter()

    if database == "neo4j":
        return Neo4jAdapter()

    raise NotImplementedError(
        f"Adapter for '{database}' has not been implemented yet."
    )


def run_single_query(adapter, workload):
    """
    Execute one workload and measure end-to-end latency.

    Timing includes:
    - sending the query
    - database execution
    - receiving results
    - materializing returned records
    """

    start = time.perf_counter()

    records = adapter.execute_query(
        workload.query,
        workload.parameters,
    )

    elapsed = time.perf_counter() - start

    latency_ms = elapsed * 1000

    return latency_ms, len(records)


def run_benchmark(
    adapter,
    database,
    warmup_runs,
    measured_runs,
    workloads,
):
    """
    Execute all workloads and return raw benchmark records.
    """

    results = []

    timestamp = datetime.now(timezone.utc).isoformat()

    print()
    print("=" * 60)
    print("Benchmark execution")
    print("=" * 60)

    print(f"Database: {database}")
    print(f"Workloads: {len(workloads)}")
    print(f"Warmup runs: {warmup_runs}")
    print(f"Measured runs: {measured_runs}")

    for workload in workloads:

        print()
        print("-" * 60)
        print(f"Workload: {workload.name}")
        print(f"Description: {workload.description}")

        # -------------------------------------------------
        # Warm-up
        # -------------------------------------------------

        print("Warm-up:", end=" ")

        for i in range(warmup_runs):

            try:
                run_single_query(
                    adapter,
                    workload,
                )

                print(
                    f"{i + 1}",
                    end=" ",
                    flush=True,
                )

            except Exception as exc:

                print()
                print(
                    f"Warm-up failed: {type(exc).__name__}: {exc}"
                )

        print()

        # -------------------------------------------------
        # Measured runs
        # -------------------------------------------------

        for run_number in range(1, measured_runs + 1):

            print(
                f"Run {run_number}/{measured_runs}: ",
                end="",
                flush=True,
            )

            start_time = datetime.now(timezone.utc)

            try:

                latency_ms, record_count = run_single_query(
                    adapter,
                    workload,
                )

                result = {
                    "timestamp_utc": start_time.isoformat(),
                    "database": database,
                    "workload": workload.name,
                    "description": workload.description,
                    "run": run_number,
                    "status": "success",
                    "latency_ms": round(latency_ms, 3),
                    "record_count": record_count,
                    "error": "",
                }

                results.append(result)

                print(
                    f"{latency_ms:.3f} ms "
                    f"({record_count} records)"
                )

            except Exception as exc:

                result = {
                    "timestamp_utc": start_time.isoformat(),
                    "database": database,
                    "workload": workload.name,
                    "description": workload.description,
                    "run": run_number,
                    "status": "error",
                    "latency_ms": "",
                    "record_count": "",
                    "error": f"{type(exc).__name__}: {exc}",
                }

                results.append(result)

                print(
                    f"ERROR: {type(exc).__name__}: {exc}"
                )

    return results


def save_raw_results(results, database, dataset):

    output_file = (
    RAW_RESULTS_DIR
    / f"{database}_{dataset}_benchmark.csv"
  )

    fieldnames = [
        "timestamp_utc",
        "database",
        "workload",
        "description",
        "run",
        "status",
        "latency_ms",
        "record_count",
        "error",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(results)

    return output_file


def print_summary(results):

    print()
    print("=" * 60)
    print("Benchmark Summary")
    print("=" * 60)

    successful = [
        row
        for row in results
        if row["status"] == "success"
    ]

    errors = [
        row
        for row in results
        if row["status"] == "error"
    ]

    print(
        f"Total measurements: {len(results):,}"
    )

    print(
        f"Successful: {len(successful):,}"
    )

    print(
        f"Errors: {len(errors):,}"
    )

    if not successful:
        print()
        print("No successful benchmark measurements.")
        return

    latencies = [
        float(row["latency_ms"])
        for row in successful
    ]

    average = sum(latencies) / len(latencies)

    minimum = min(latencies)
    maximum = max(latencies)

    sorted_latencies = sorted(latencies)

    p95_index = int(
        0.95 * (len(sorted_latencies) - 1)
    )

    p95 = sorted_latencies[p95_index]

    print(
        f"Average latency: {average:.3f} ms"
    )

    print(
        f"Minimum latency: {minimum:.3f} ms"
    )

    print(
        f"Maximum latency: {maximum:.3f} ms"
    )

    print(
        f"P95 latency: {p95:.3f} ms"
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "CognoDB Cloud Graph Database Benchmark"
        )
    )

    parser.add_argument(
        "--database",
        required=True,
        choices=SUPPORTED_DATABASES,
        help="Database to benchmark",
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=2,
        help="Number of warm-up runs per workload",
    )
    
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of measured runs per workload",
    )

    parser.add_argument(
        "--dataset",
        choices=["synthetic", "wikivote"],
        default="synthetic",
        help="Workload dataset to benchmark",
    )

    args = parser.parse_args()

    if args.dataset == "wikivote":
        workloads = WIKIVOTE_WORKLOADS
    else:
        workloads = DEFAULT_WORKLOADS

    if args.warmup < 0:
        parser.error("--warmup cannot be negative")

    if args.runs <= 0:
        parser.error("--runs must be greater than zero")

    print("=" * 60)
    print("CognoDB Cloud Graph Database Benchmark")
    print("=" * 60)

    print(
        f"Selected database: {args.database}"
    )

    print(
        f"Warm-up runs: {args.warmup}"
    )

    print(
        f"Measured runs: {args.runs}"
    )

    adapter = create_adapter(
        args.database
    )

    try:

        print()
        print("Connecting to database...")

        adapter.connect()

        print(
            "Database connection successful!"
        )

        results = run_benchmark(
    adapter=adapter,
    database=args.database,
    warmup_runs=args.warmup,
    measured_runs=args.runs,
    workloads=workloads,
)
        output_file = save_raw_results(
    results,
    args.database,
    args.dataset,

    )

        print_summary(results)

        print()
        print("=" * 60)
        print("Raw results saved")
        print("=" * 60)

        print(output_file)

    finally:

        adapter.close()

        print()
        print(
            "Database connection closed."
        )


if __name__ == "__main__":
    main()