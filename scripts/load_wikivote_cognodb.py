import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "wiki-vote-edges.csv"


# =========================================================
# Environment
# =========================================================

load_dotenv(BASE_DIR / ".env")

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


if not URI:
    raise RuntimeError("COGNODB_URI is missing from .env")

if not USERNAME:
    raise RuntimeError("COGNODB_USERNAME is missing from .env")

if not PASSWORD:
    raise RuntimeError("COGNODB_PASSWORD is missing from .env")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )


# =========================================================
# Read Dataset
# =========================================================

def read_edges():
    with DATA_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


# =========================================================
# Load Wiki-Vote
# =========================================================

def load_wikivote(session, rows, batch_size=1000):

    total = len(rows)

    print()
    print("Loading Wiki-Vote relationships...")
    print("-" * 60)

    start_time = time.perf_counter()

    for start in range(0, total, batch_size):

        batch = rows[start:start + batch_size]

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


# =========================================================
# Create Index
# =========================================================

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


# =========================================================
# Verification
# =========================================================

def verify_database(session):

    print()
    print("=" * 60)
    print("Wiki-Vote Verification")
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

    nodes = node_result["count"]
    relationships = relationship_result["count"]

    print(f"WikiUser nodes: {nodes:,}")
    print(f"VOTES relationships: {relationships:,}")

    print()
    print("=" * 60)


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 60)
    print("CognoDB Wiki-Vote Dataset Loader")
    print("=" * 60)

    print()
    print(f"Dataset: {DATA_FILE}")

    rows = read_edges()

    print(
        f"Dataset relationships: {len(rows):,}"
    )

    print()
    print("Connecting to CognoDB...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        print(
            "CognoDB connection successful!"
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
    print("Wiki-Vote loading completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()