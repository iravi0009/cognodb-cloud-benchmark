import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "wiki-vote-edges.csv"

load_dotenv(BASE_DIR / ".env")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not URI:
    raise RuntimeError("NEO4J_URI is missing from .env")

if not USERNAME:
    raise RuntimeError("NEO4J_USERNAME is missing from .env")

if not PASSWORD:
    raise RuntimeError("NEO4J_PASSWORD is missing from .env")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")


def read_edges():
    with DATA_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def create_index(session):
    print()
    print("Creating WikiUser index...")

    session.run(
        """
        CREATE INDEX wikiuser_id_index IF NOT EXISTS
        FOR (u:WikiUser)
        ON (u.id)
        """
    ).consume()

    print("Index created/verified.")


def load_wikivote(session, rows, batch_size=1000):

    total = len(rows)

    print()
    print("Loading Wiki-Vote into Neo4j...")
    print("-" * 60)

    start_time = time.perf_counter()

    query = """
    UNWIND $rows AS row

    MERGE (source:WikiUser {
        id: toInteger(row.source)
    })

    MERGE (target:WikiUser {
        id: toInteger(row.target)
    })

    MERGE (source)-[:VOTES]->(target)
    """

    for start in range(0, total, batch_size):

        batch = rows[start:start + batch_size]

        session.run(
            query,
            rows=batch,
        ).consume()

        processed = min(
            start + batch_size,
            total,
        )

        print(
            f"  Processed {processed:,}/{total:,}",
            flush=True,
        )

    elapsed = time.perf_counter() - start_time

    throughput = (
        total / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(f"Relationships loaded: {total:,}")
    print(f"Load time: {elapsed:.3f} seconds")
    print(
        f"Relationship throughput: "
        f"{throughput:,.2f} relationships/sec"
    )

    return elapsed, throughput


def verify_database(session):

    print()
    print("=" * 60)
    print("Neo4j Wiki-Vote Verification")
    print("=" * 60)

    node_result = session.run(
        """
        MATCH (n:WikiUser)
        RETURN count(n) AS count
        """
    ).single()

    relationship_result = session.run(
        """
        MATCH ()-[r:VOTES]->()
        RETURN count(r) AS count
        """
    ).single()

    print(
        f"WikiUser nodes: "
        f"{node_result['count']:,}"
    )

    print(
        f"VOTES relationships: "
        f"{relationship_result['count']:,}"
    )

    print("=" * 60)


def main():

    print("=" * 60)
    print("Neo4j Wiki-Vote Dataset Loader")
    print("=" * 60)

    rows = read_edges()

    print()
    print(
        f"Dataset relationships: "
        f"{len(rows):,}"
    )

    print()
    print("Connecting to Neo4j...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        print(
            "Neo4j connection successful!"
        )

        with driver.session() as session:

            create_index(session)

            load_wikivote(
                session,
                rows,
            )

            verify_database(session)

    finally:

        driver.close()

    print()
    print("=" * 60)
    print("Neo4j Wiki-Vote loading completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()