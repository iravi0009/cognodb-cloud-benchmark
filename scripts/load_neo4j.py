import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def read_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def run_query_in_batches(
    session,
    query,
    rows,
    batch_size=500,
):
    total = len(rows)

    for start in range(0, total, batch_size):

        batch = rows[start:start + batch_size]

        session.run(
            query,
            rows=batch,
        ).consume()

        end = min(
            start + batch_size,
            total,
        )

        print(
            f"  Processed {end:,}/{total:,}"
        )


# ---------------------------------------------------------
# Indexes
# ---------------------------------------------------------

def create_indexes(session):

    print()
    print("Creating indexes...")
    print("-" * 40)

    indexes = [
        """
        CREATE INDEX person_id_index IF NOT EXISTS
        FOR (p:Person)
        ON (p.id)
        """,
        """
        CREATE INDEX company_id_index IF NOT EXISTS
        FOR (c:Company)
        ON (c.id)
        """,
        """
        CREATE INDEX technology_id_index IF NOT EXISTS
        FOR (t:Technology)
        ON (t.id)
        """,
    ]

    for query in indexes:
        session.run(query).consume()

    print("Indexes created/verified.")


# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

def load_persons(session):

    rows = read_csv("persons.csv")

    query = """
    UNWIND $rows AS row

    MERGE (p:Person {id: row.id})

    SET
        p.name = row.name,
        p.age = toInteger(row.age),
        p.city = row.city,
        p.role = row.role
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"Persons loaded: {len(rows):,}"
    )


def load_companies(session):

    rows = read_csv("companies.csv")

    query = """
    UNWIND $rows AS row

    MERGE (c:Company {id: row.id})

    SET
        c.name = row.name,
        c.industry = row.industry,
        c.size = toInteger(row.size)
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"Companies loaded: {len(rows):,}"
    )


def load_technologies(session):

    rows = read_csv("technologies.csv")

    query = """
    UNWIND $rows AS row

    MERGE (t:Technology {id: row.id})

    SET
        t.name = row.name,
        t.category = row.category
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"Technologies loaded: {len(rows):,}"
    )


# ---------------------------------------------------------
# Relationships
# ---------------------------------------------------------

def load_works_at(session):

    rows = read_csv("works_at.csv")

    query = """
    UNWIND $rows AS row

    MATCH (p:Person {id: row.person_id})
    MATCH (c:Company {id: row.company_id})

    MERGE (p)-[r:WORKS_AT]->(c)

    SET
        r.since = toInteger(row.since),
        r.position = row.position
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"WORKS_AT relationships loaded: {len(rows):,}"
    )


def load_knows(session):

    rows = read_csv("knows.csv")

    query = """
    UNWIND $rows AS row

    MATCH (a:Person {id: row.person_a})
    MATCH (b:Person {id: row.person_b})

    MERGE (a)-[r:KNOWS]->(b)

    SET
        r.since = toInteger(row.since),
        r.strength = toInteger(row.strength)
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"KNOWS relationships loaded: {len(rows):,}"
    )


def load_person_uses(session):

    rows = read_csv("person_uses.csv")

    query = """
    UNWIND $rows AS row

    MATCH (p:Person {id: row.person_id})
    MATCH (t:Technology {id: row.technology_id})

    MERGE (p)-[r:USES]->(t)

    SET
        r.years = toInteger(row.years),
        r.proficiency = toInteger(row.proficiency)
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"Person USES relationships loaded: "
        f"{len(rows):,}"
    )


def load_company_uses(session):

    rows = read_csv("company_uses.csv")

    query = """
    UNWIND $rows AS row

    MATCH (c:Company {id: row.company_id})
    MATCH (t:Technology {id: row.technology_id})

    MERGE (c)-[r:USES]->(t)

    SET
        r.years = toInteger(row.years),
        r.proficiency = toInteger(row.proficiency)
    """

    run_query_in_batches(
        session,
        query,
        rows,
    )

    print(
        f"Company USES relationships loaded: "
        f"{len(rows):,}"
    )


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

def verify_database(session):

    print()
    print("=" * 60)
    print("Neo4j Aura Graph Verification")
    print("=" * 60)

    node_result = session.run(
        """
        MATCH (n)
        RETURN count(n) AS total_nodes
        """
    ).single()

    relationship_result = session.run(
        """
        MATCH ()-[r]->()
        RETURN count(r) AS total_relationships
        """
    ).single()

    total_nodes = node_result["total_nodes"]
    total_relationships = (
        relationship_result["total_relationships"]
    )

    print(
        f"Total nodes: {total_nodes:,}"
    )

    print(
        f"Total relationships: "
        f"{total_relationships:,}"
    )

    print()
    print("Nodes by label:")

    result = session.run(
        """
        MATCH (n)
        RETURN labels(n) AS labels,
               count(n) AS count
        ORDER BY count DESC
        """
    )

    for record in result:

        print(
            f"  {record['labels']}: "
            f"{record['count']:,}"
        )

    print()
    print("Relationships by type:")

    result = session.run(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS type,
               count(r) AS count
        ORDER BY count DESC
        """
    )

    for record in result:

        print(
            f"  {record['type']}: "
            f"{record['count']:,}"
        )

    return total_nodes, total_relationships


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("Neo4j Aura Benchmark Dataset Loader")
    print("=" * 60)

    print()
    print(
        f"Data directory: {DATA_DIR}"
    )

    print()
    print("Connecting to Neo4j Aura...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        print(
            "Neo4j Aura connection successful!"
        )

        with driver.session() as session:

            create_indexes(session)

            print()
            print("Loading nodes...")
            print("-" * 40)

            load_persons(session)
            load_companies(session)
            load_technologies(session)

            print()
            print("Loading relationships...")
            print("-" * 40)

            load_works_at(session)
            load_knows(session)
            load_person_uses(session)
            load_company_uses(session)

            verify_database(session)

    finally:

        driver.close()

        print()
        print(
            "Neo4j Aura connection closed."
        )

    print()
    print("=" * 60)
    print(
        "Neo4j Aura dataset loading completed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()