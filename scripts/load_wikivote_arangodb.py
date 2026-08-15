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
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")


def main():
    with DATA_FILE.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    user_ids = sorted({r["source"] for r in rows} | {r["target"] for r in rows})
    users = [{"_key": uid, "id": int(uid)} for uid in user_ids]
    edges = [
        {
            "_key": f"{r['source']}_{r['target']}",
            "_from": f"wikivote_users/{r['source']}",
            "_to": f"wikivote_users/{r['target']}",
        }
        for r in rows
    ]

    client = ArangoClient(hosts=URL)
    db = client.db(DATABASE, username=USERNAME, password=PASSWORD)

    for name, edge in [("wikivote_users", False), ("wikivote_votes", True)]:
        if db.has_collection(name):
            db.collection(name).truncate()
        else:
            db.create_collection(name, edge=edge)

    users_collection = db.collection("wikivote_users")
    votes_collection = db.collection("wikivote_votes")

    start = time.perf_counter()
    users_collection.import_bulk(users, on_duplicate="replace")
    votes_collection.import_bulk(edges, on_duplicate="replace")
    elapsed = time.perf_counter() - start

    if not users_collection.index("wikivote_id_index"):
        users_collection.add_index({"type": "persistent", "fields": ["id"], "name": "wikivote_id_index"})

    user_count = db.aql.execute("RETURN LENGTH(wikivote_users)").next()
    edge_count = db.aql.execute("RETURN LENGTH(wikivote_votes)").next()

    print("=" * 60)
    print("ArangoDB Wiki-Vote Verification")
    print("=" * 60)
    print(f"WikiUser nodes: {user_count:,}")
    print(f"VOTES relationships: {edge_count:,}")
    print(f"Load time: {elapsed:.3f} seconds")
    print(f"Nodes/sec: {user_count / elapsed:,.2f}")
    print(f"Relationships/sec: {edge_count / elapsed:,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
