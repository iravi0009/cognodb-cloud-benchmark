import csv
import os
import time
from pathlib import Path

from arango import ArangoClient
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "wiki-vote-edges.csv"

load_dotenv(BASE_DIR / ".env")


URL = os.getenv("ARANGODB_URL")
USERNAME = os.getenv("ARANGODB_USERNAME", "root")
PASSWORD = os.getenv("ARANGODB_PASSWORD")
DATABASE = os.getenv("ARANGODB_DATABASE", "_system")


if not URL:
    raise RuntimeError("ARANGODB_URL is missing from .env")

if not PASSWORD:
    raise RuntimeError("ARANGODB_PASSWORD is missing from .env")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )


def main():

    print("=" * 60)
    print("ArangoDB Wiki-Vote Loader")
    print("=" * 60)

    print(f"URL: {URL}")
    print(f"Database: {DATABASE}")
    print(f"Dataset: {DATA_FILE}")
    print()

    # -------------------------------------------------
    # Load CSV
    # -------------------------------------------------

    print("Reading Wiki-Vote dataset...")

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(csv.DictReader(file))

    print(f"CSV rows loaded: {len(rows):,}")

    # -------------------------------------------------
    # Prepare users
    # -------------------------------------------------

    user_ids = sorted(
        {row["source"] for row in rows}
        |
        {row["target"] for row in rows}
    )

    users = [
        {
            "_key": user_id,
            "id": int(user_id),
        }
        for user_id in user_ids
    ]

    # -------------------------------------------------
    # Prepare edges
    # -------------------------------------------------

    edges = [
        {
            "_key": f"{row['source']}_{row['target']}",
            "_from": f"wikivote_users/{row['source']}",
            "_to": f"wikivote_users/{row['target']}",
        }
        for row in rows
    ]

    print(f"WikiUser nodes prepared: {len(users):,}")
    print(f"VOTES relationships prepared: {len(edges):,}")
    print()

    # -------------------------------------------------
    # Connect to ArangoDB
    # -------------------------------------------------

    print("Connecting to ArangoDB...")

    client = ArangoClient(hosts=URL)

    db = client.db(
        DATABASE,
        username=USERNAME,
        password=PASSWORD,
    )

    print("ArangoDB connection successful!")
    print()

    # -------------------------------------------------
    # Create / reset collections
    # -------------------------------------------------

    print("Preparing collections...")

    collections = [
        ("wikivote_users", False),
        ("wikivote_votes", True),
    ]

    for name, edge in collections:

        if db.has_collection(name):

            print(f"Truncating existing collection: {name}")

            db.collection(name).truncate()

        else:

            print(f"Creating collection: {name}")

            db.create_collection(
                name,
                edge=edge,
            )

    users_collection = db.collection(
        "wikivote_users"
    )

    votes_collection = db.collection(
        "wikivote_votes"
    )

    print()

    # -------------------------------------------------
    # Bulk import
    # -------------------------------------------------

    print("Importing Wiki-Vote data...")

    start = time.perf_counter()

    users_collection.import_bulk(
        users,
        on_duplicate="replace",
    )

    votes_collection.import_bulk(
        edges,
        on_duplicate="replace",
    )

    elapsed = time.perf_counter() - start

    print(
        f"Import completed in {elapsed:.3f} seconds."
    )

    # -------------------------------------------------
    # Create index
    # -------------------------------------------------

    print("Checking Wiki-Vote index...")

    existing_indexes = users_collection.indexes()

    index_exists = any(
        index.get("name") == "wikivote_id_index"
        for index in existing_indexes
    )

    if not index_exists:

        print("Creating wikivote_id_index...")

        users_collection.add_index(
            {
                "type": "persistent",
                "fields": ["id"],
                "name": "wikivote_id_index",
            }
        )

    else:

        print("wikivote_id_index already exists.")

    # -------------------------------------------------
    # Verification
    # -------------------------------------------------

    print()
    print("Verifying loaded data...")

    user_count = db.aql.execute(
        "RETURN LENGTH(wikivote_users)"
    ).next()

    edge_count = db.aql.execute(
        "RETURN LENGTH(wikivote_votes)"
    ).next()

    # -------------------------------------------------
    # Results
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("ArangoDB Wiki-Vote Verification")
    print("=" * 60)

    print(
        f"WikiUser nodes: {user_count:,}"
    )

    print(
        f"VOTES relationships: {edge_count:,}"
    )

    print(
        f"Load time: {elapsed:.3f} seconds"
    )

    if elapsed > 0:

        print(
            f"Nodes/sec: "
            f"{user_count / elapsed:,.2f}"
        )

        print(
            f"Relationships/sec: "
            f"{edge_count / elapsed:,.2f}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()