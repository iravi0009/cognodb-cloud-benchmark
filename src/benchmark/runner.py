import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

from .adapters.arangodb import ArangoDBAdapter
from .adapters.cognodb import CognoDBAdapter
from .adapters.neo4j import Neo4jAdapter
from .adapters.memgraph import MemgraphAdapter
from .adapters.falkordb import FalkorDBAdapter
from .workloads.queries import WORKLOADS as DEFAULT_WORKLOADS
from .workloads.wikivote_queries import WORKLOADS as WIKIVOTE_WORKLOADS
from .workloads.arangodb_wikivote_queries import WORKLOADS as ARANGODB_WIKIVOTE_WORKLOADS

SUPPORTED_DATABASES = ["cognodb", "neo4j", "memgraph", "falkordb", "arangodb"]
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_RESULTS_DIR = BASE_DIR / "results" / "raw"
RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def create_adapter(database):
    return {
        "cognodb": CognoDBAdapter,
        "neo4j": Neo4jAdapter,
        "memgraph": MemgraphAdapter,
        "falkordb": FalkorDBAdapter,
        "arangodb": ArangoDBAdapter,
    }[database]()


def run_single_query(adapter, workload):
    start = time.perf_counter()
    records = adapter.execute_query(workload.query, workload.parameters)
    return (time.perf_counter() - start) * 1000, len(records)


def run_benchmark(adapter, database, warmup_runs, measured_runs, workloads):
    results = []
    print("\n" + "=" * 60)
    print("Benchmark execution")
    print("=" * 60)
    print(f"Database: {database}")
    print(f"Workloads: {len(workloads)}")
    print(f"Warmup runs: {warmup_runs}")
    print(f"Measured runs: {measured_runs}")
    for workload in workloads:
        print("\n" + "-" * 60)
        print(f"Workload: {workload.name}")
        print(f"Description: {workload.description}")
        print("Warm-up:", end=" ")
        for i in range(warmup_runs):
            try:
                run_single_query(adapter, workload)
                print(i + 1, end=" ", flush=True)
            except Exception as exc:
                print(f"FAILED({type(exc).__name__}: {exc})", end=" ", flush=True)
        print()
        for run_number in range(1, measured_runs + 1):
            print(f"Run {run_number}/{measured_runs}: ", end="", flush=True)
            started = datetime.now(timezone.utc)
            try:
                latency, count = run_single_query(adapter, workload)
                results.append({"timestamp_utc": started.isoformat(), "database": database, "workload": workload.name, "description": workload.description, "run": run_number, "status": "success", "latency_ms": round(latency, 3), "record_count": count, "error": ""})
                print(f"{latency:.3f} ms ({count} records)")
            except Exception as exc:
                results.append({"timestamp_utc": started.isoformat(), "database": database, "workload": workload.name, "description": workload.description, "run": run_number, "status": "error", "latency_ms": "", "record_count": "", "error": f"{type(exc).__name__}: {exc}"})
                print(f"ERROR: {type(exc).__name__}: {exc}")
    return results


def save_raw_results(results, database, dataset):
    path = RAW_RESULTS_DIR / f"{database}_{dataset}_benchmark.csv"
    fields = ["timestamp_utc", "database", "workload", "description", "run", "status", "latency_ms", "record_count", "error"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    return path


def print_summary(results):
    print("\n" + "=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    successful = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    print(f"Total measurements: {len(results):,}")
    print(f"Successful: {len(successful):,}")
    print(f"Errors: {len(errors):,}")
    if not successful:
        print("No successful benchmark measurements.")
        return
    values = sorted(float(r["latency_ms"]) for r in successful)
    def pct(p):
        if len(values) == 1:
            return values[0]
        index = p * (len(values) - 1)
        lo = int(index)
        hi = min(lo + 1, len(values) - 1)
        return values[lo] + (values[hi] - values[lo]) * (index - lo)
    print(f"Average latency: {sum(values) / len(values):.3f} ms")
    print(f"Median / P50 latency: {pct(.50):.3f} ms")
    print(f"Minimum latency: {values[0]:.3f} ms")
    print(f"Maximum latency: {values[-1]:.3f} ms")
    print(f"P95 latency: {pct(.95):.3f} ms")
    print(f"P99 latency: {pct(.99):.3f} ms")


def main():
    parser = argparse.ArgumentParser(description="CognoDB Cloud Graph Database Benchmark")
    parser.add_argument("--database", required=True, choices=SUPPORTED_DATABASES)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--dataset", choices=["synthetic", "wikivote"], default="wikivote")
    args = parser.parse_args()
    if args.warmup < 0:
        parser.error("--warmup cannot be negative")
    if args.runs <= 0:
        parser.error("--runs must be greater than zero")
    if args.dataset == "wikivote":
        workloads = ARANGODB_WIKIVOTE_WORKLOADS if args.database == "arangodb" else WIKIVOTE_WORKLOADS
    else:
        workloads = DEFAULT_WORKLOADS
    print("=" * 60)
    print("CognoDB Cloud Graph Database Benchmark")
    print("=" * 60)
    print(f"Selected database: {args.database}")
    print(f"Warm-up runs: {args.warmup}")
    print(f"Measured runs: {args.runs}")
    print(f"Dataset: {args.dataset}")
    adapter = create_adapter(args.database)
    try:
        print("\nConnecting to database...")
        adapter.connect()
        results = run_benchmark(adapter, args.database, args.warmup, args.runs, workloads)
        output = save_raw_results(results, args.database, args.dataset)
        print_summary(results)
        print("\nRaw results saved")
        print(output)
    finally:
        adapter.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()
