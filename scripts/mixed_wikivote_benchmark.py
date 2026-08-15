import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.benchmark.adapters.arangodb import ArangoDBAdapter
from src.benchmark.adapters.cognodb import CognoDBAdapter
from src.benchmark.adapters.neo4j import Neo4jAdapter
from src.benchmark.adapters.memgraph import MemgraphAdapter
from src.benchmark.adapters.falkordb import FalkorDBAdapter


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "wiki-vote-edges.csv"


ADAPTERS = {
    "cognodb": CognoDBAdapter,
    "neo4j": Neo4jAdapter,
    "memgraph": MemgraphAdapter,
    "falkordb": FalkorDBAdapter,
    "arangodb": ArangoDBAdapter,
}


# ---------------------------------------------------------
# Load actual Wiki-Vote user IDs
# ---------------------------------------------------------

def load_user_ids():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Wiki-Vote dataset not found: {DATA_FILE}"
        )

    user_ids = set()

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            user_ids.add(int(row["source"]))
            user_ids.add(int(row["target"]))

    user_ids = sorted(user_ids)

    if not user_ids:
        raise RuntimeError(
            "No Wiki-Vote user IDs found in dataset."
        )

    return user_ids


# ---------------------------------------------------------
# Database-specific queries
# ---------------------------------------------------------

def build_queries(database, user_id, write_value):
    """
    Build equivalent logical read/write operations
    for each graph database.
    """

    if database == "arangodb":

        read_query = """
        FOR u IN wikivote_users
            FILTER u._key == @user_id
            RETURN u._key
        """

        write_query = """
        UPDATE @user_id
        WITH {
            benchmark_touch: @touch
        }
        IN wikivote_users
        RETURN NEW._key
        """

        return (
            read_query,
            {
                "user_id": str(user_id),
            },
            write_query,
            {
                "user_id": str(user_id),
                "touch": write_value,
            },
        )

    if database == "falkordb":

        read_query = (
            f"MATCH (u:WikiUser {{id: {user_id}}}) "
            "RETURN u.id"
        )

        write_query = (
            f"MATCH (u:WikiUser {{id: {user_id}}}) "
            f"SET u.benchmark_touch = {write_value} "
            "RETURN u.id"
        )

        return (
            read_query,
            {},
            write_query,
            {},
        )

    read_query = """
    MATCH (u:WikiUser {id: $user_id})
    RETURN u.id
    """

    write_query = """
    MATCH (u:WikiUser {id: $user_id})
    SET u.benchmark_touch = $touch
    RETURN u.id
    """

    return (
        read_query,
        {
            "user_id": user_id,
        },
        write_query,
        {
            "user_id": user_id,
            "touch": write_value,
        },
    )


# ---------------------------------------------------------
# Worker
# ---------------------------------------------------------

def worker(
    database,
    operations,
    worker_id,
    user_ids,
):
    """
    Each worker receives its own deterministic slice of
    Wiki-Vote users.

    This avoids making every concurrent writer update the
    same document and creating an artificial hotspot.
    """

    adapter = ADAPTERS[database]()
    adapter.connect()

    successes = 0
    errors = 0
    error_messages = []

    try:

        for operation_number in range(operations):

            # -------------------------------------------------
            # Select a user belonging to this worker.
            #
            # Different workers use different positions in
            # the user list, reducing artificial write
            # contention.
            # -------------------------------------------------

            user_index = (
                worker_id
                + operation_number
                * max(1, worker_count_for_assignment)
            ) % len(user_ids)

            user_id = user_ids[user_index]

            # -------------------------------------------------
            # 80% READ / 20% WRITE
            #
            # Deterministic rather than random:
            # operations 0-3 = reads
            # operation 4   = write
            # repeated.
            # -------------------------------------------------

            is_read = (
                operation_number % 5 != 4
            )

            try:

                write_value = int(
                    time.time_ns()
                    % 1_000_000_000
                )

                (
                    read_query,
                    read_params,
                    write_query,
                    write_params,
                ) = build_queries(
                    database,
                    user_id,
                    write_value,
                )

                if is_read:

                    adapter.execute_query(
                        read_query,
                        read_params,
                    )

                else:

                    adapter.execute_query(
                        write_query,
                        write_params,
                    )

                successes += 1

            except Exception as exc:

                errors += 1

                if len(error_messages) < 3:

                    error_messages.append(
                        f"{type(exc).__name__}: {exc}"
                    )

        return {
            "worker_id": worker_id,
            "successes": successes,
            "errors": errors,
            "error_messages": error_messages,
        }

    finally:

        adapter.close()


# ---------------------------------------------------------
# Run one concurrency level
# ---------------------------------------------------------

def run(
    database,
    concurrency,
    total_operations,
    user_ids,
):
    """
    Run exactly total_operations across the selected
    concurrency level.
    """

    global worker_count_for_assignment

    worker_count_for_assignment = concurrency

    # -----------------------------------------------------
    # Divide operations as evenly as possible.
    # -----------------------------------------------------

    base_operations = (
        total_operations // concurrency
    )

    remainder = (
        total_operations % concurrency
    )

    operations_per_worker = []

    for worker_id in range(concurrency):

        operations = base_operations

        if worker_id < remainder:
            operations += 1

        operations_per_worker.append(
            operations
        )

    # -----------------------------------------------------
    # Start timer
    # -----------------------------------------------------

    start = time.perf_counter()

    successes = 0
    errors = 0
    error_messages = []

    # -----------------------------------------------------
    # Start workers
    # -----------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as pool:

        futures = []

        for worker_id, operations in enumerate(
            operations_per_worker
        ):

            if operations == 0:
                continue

            futures.append(
                pool.submit(
                    worker,
                    database,
                    operations,
                    worker_id,
                    user_ids,
                )
            )

        # -------------------------------------------------
        # Collect results
        # -------------------------------------------------

        for future in as_completed(futures):

            result = future.result()

            successes += result["successes"]
            errors += result["errors"]

            error_messages.extend(
                result["error_messages"]
            )

    elapsed = (
        time.perf_counter() - start
    )

    throughput = (
        successes / elapsed
        if elapsed > 0
        else 0
    )

    return (
        elapsed,
        successes,
        errors,
        throughput,
        error_messages,
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Wiki-Vote concurrent mixed "
            "read/write benchmark"
        )
    )

    parser.add_argument(
        "--database",
        required=True,
        choices=ADAPTERS.keys(),
    )

    parser.add_argument(
        "--operations",
        type=int,
        default=400,
    )

    args = parser.parse_args()

    if args.operations <= 0:
        parser.error(
            "--operations must be greater than zero."
        )

    print("=" * 78)

    print(
        "Wiki-Vote Mixed Read/Write "
        "Concurrency Benchmark"
    )

    print("=" * 78)

    print(
        f"Database: {args.database}"
    )

    print(
        "Read/write mix: 80% reads / 20% writes"
    )

    print(
        f"Operations per concurrency level: "
        f"{args.operations}"
    )

    print(
        "Concurrency levels: 1 / 10 / 40"
    )

    print(
        "Write contention mitigation: "
        "worker-specific user distribution"
    )

    print("=" * 78)

    print()

    # -----------------------------------------------------
    # Load dataset user IDs
    # -----------------------------------------------------

    user_ids = load_user_ids()

    print(
        f"Wiki-Vote users available: "
        f"{len(user_ids):,}"
    )

    print()

    # -----------------------------------------------------
    # Required concurrency sweep
    # -----------------------------------------------------

    for concurrency in (1, 10, 40):

        print(
            "-" * 78
        )

        print(
            f"Starting concurrency={concurrency}"
        )

        (
            elapsed,
            successes,
            errors,
            throughput,
            error_messages,
        ) = run(
            database=args.database,
            concurrency=concurrency,
            total_operations=args.operations,
            user_ids=user_ids,
        )

        print()

        print(
            f"Concurrency={concurrency:>2} | "
            f"Elapsed={elapsed:.3f}s | "
            f"Successful={successes} | "
            f"Errors={errors} | "
            f"Throughput={throughput:.2f} "
            f"queries/sec"
        )

        # -------------------------------------------------
        # Diagnostic errors
        # -------------------------------------------------

        if error_messages:

            print(
                "Sample errors:"
            )

            for message in error_messages[:5]:

                print(
                    f"  {message}"
                )

        print()

    print("=" * 78)

    print(
        "Concurrency benchmark completed."
    )

    print("=" * 78)


if __name__ == "__main__":
    main()