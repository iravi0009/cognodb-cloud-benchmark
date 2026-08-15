import argparse
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.benchmark.adapters.arangodb import ArangoDBAdapter
from src.benchmark.adapters.cognodb import CognoDBAdapter
from src.benchmark.adapters.neo4j import Neo4jAdapter
from src.benchmark.adapters.memgraph import MemgraphAdapter
from src.benchmark.adapters.falkordb import FalkorDBAdapter


ADAPTERS = {
    "cognodb": CognoDBAdapter,
    "neo4j": Neo4jAdapter,
    "memgraph": MemgraphAdapter,
    "falkordb": FalkorDBAdapter,
    "arangodb": ArangoDBAdapter,
}


def queries(database, write_value):
    if database == "arangodb":
        return (
            "FOR u IN wikivote_users FILTER u._key == @user_id RETURN u._key",
            "UPDATE @user_id WITH {benchmark_touch: @touch} IN wikivote_users RETURN NEW._key",
        ), {"user_id": "3", "touch": write_value}

    if database == "falkordb":
        return (
            "MATCH (u:WikiUser {id: 3}) RETURN u.id",
            f"MATCH (u:WikiUser {{id: 3}}) SET u.benchmark_touch = {write_value} RETURN u.id",
        ), {}

    return (
        "MATCH (u:WikiUser {id: $user_id}) RETURN u.id",
        "MATCH (u:WikiUser {id: $user_id}) SET u.benchmark_touch = $touch RETURN u.id",
    ), {"user_id": 3, "touch": write_value}


def worker(database, operations):
    adapter = ADAPTERS[database]()
    adapter.connect()
    try:
        successes = 0
        errors = 0
        read_query, write_query = queries(database, int(time.time_ns() % 1_000_000_000))
        params = {"user_id": 3}
        for _ in range(operations):
            try:
                if random.random() < 0.80:
                    adapter.execute_query(read_query, params)
                else:
                    write_value = int(time.time_ns() % 1_000_000_000)
                    if database == "arangodb":
                        adapter.execute_query(write_query, {"user_id": "3", "touch": write_value})
                    elif database == "falkordb":
                        adapter.execute_query(
                            f"MATCH (u:WikiUser {{id: 3}}) SET u.benchmark_touch = {write_value} RETURN u.id",
                            {},
                        )
                    else:
                        adapter.execute_query(write_query, {"user_id": 3, "touch": write_value})
                successes += 1
            except Exception:
                errors += 1
        return successes, errors
    finally:
        adapter.close()


def run(database, concurrency, total_operations):
    per_client = total_operations // concurrency
    start = time.perf_counter()
    successes = errors = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(worker, database, per_client) for _ in range(concurrency)]
        for future in as_completed(futures):
            ok, bad = future.result()
            successes += ok
            errors += bad
    elapsed = time.perf_counter() - start
    qps = successes / elapsed if elapsed else 0
    return elapsed, successes, errors, qps


def main():
    parser = argparse.ArgumentParser(description="Wiki-Vote concurrent mixed read/write benchmark")
    parser.add_argument("--database", required=True, choices=ADAPTERS)
    parser.add_argument("--operations", type=int, default=400)
    args = parser.parse_args()

    print("=" * 70)
    print(f"Mixed Wiki-Vote workload: {args.database}")
    print("Read/write mix: 80% reads / 20% writes")
    print("=" * 70)

    for concurrency in (1, 10, 40):
        elapsed, successes, errors, qps = run(args.database, concurrency, args.operations)
        print(
            f"Concurrency={concurrency:>2} | "
            f"Elapsed={elapsed:.3f}s | "
            f"Successful={successes} | Errors={errors} | "
            f"Throughput={qps:.2f} queries/sec"
        )


if __name__ == "__main__":
    main()
