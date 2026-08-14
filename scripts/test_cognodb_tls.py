import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")

if not uri or not username or not password:
    raise RuntimeError("Missing CognoDB environment variables")

# Diagnostic ONLY:
# bolt+ssc = encrypted Bolt connection without certificate verification.
diagnostic_uri = uri.replace("bolt+s://", "bolt+ssc://")

print("Testing encrypted Bolt connection without certificate verification...")
print("Protocol:", diagnostic_uri.split("://")[0])

driver = GraphDatabase.driver(
    diagnostic_uri,
    auth=(username, password),
)

try:
    driver.verify_connectivity()
    print("TLS diagnostic connection successful!")

    with driver.session() as session:
        result = session.run(
            "RETURN 'CognoDB TLS diagnostic successful' AS message"
        )
        print(result.single()["message"])

finally:
    driver.close()