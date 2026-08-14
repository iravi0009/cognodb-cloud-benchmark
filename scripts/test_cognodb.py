from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt+s://db-7530b7a5.databases.cognodb.com",
    auth=("cognodb", "328b43f525a34d028a92006a364d71f3"),
)

try:
    driver.verify_connectivity()
    print("CognoDB connection successful!")
finally:
    driver.close()