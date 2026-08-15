import os
from pathlib import Path

from dotenv import dotenv_values
from neo4j import GraphDatabase


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


print("Project directory:", BASE_DIR)
print("Environment file:", ENV_FILE)
print("Environment file exists:", ENV_FILE.exists())


# ---------------------------------------------------------
# Read .env directly
# ---------------------------------------------------------

config = dotenv_values(ENV_FILE)

uri = config.get("COGNODB_URI")
username = config.get("COGNODB_USERNAME")
password = config.get("COGNODB_PASSWORD")


print()
print("URI:", uri)
print("USERNAME:", username)


# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

if not uri:
    raise RuntimeError(
        "COGNODB_URI is missing from .env"
    )

if not username:
    raise RuntimeError(
        "COGNODB_USERNAME is missing from .env"
    )

if not password:
    raise RuntimeError(
        "COGNODB_PASSWORD is missing from .env"
    )


# ---------------------------------------------------------
# Connect
# ---------------------------------------------------------

print()
print("Testing CognoDB connection...")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password),
)


try:

    driver.verify_connectivity()

    print()
    print("=" * 60)
    print("COGNODB CONNECTED SUCCESSFULLY")
    print("=" * 60)

finally:

    driver.close()

    print()
    print("Connection closed.")