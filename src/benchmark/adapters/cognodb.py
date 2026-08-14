import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from .base import GraphDatabaseAdapter


class CognoDBAdapter(GraphDatabaseAdapter):
    """
    CognoDB Cloud adapter using the Neo4j-compatible Python driver.
    """

    def __init__(self):
        load_dotenv()

        self.uri = os.getenv("COGNODB_URI")
        self.username = os.getenv("COGNODB_USERNAME")
        self.password = os.getenv("COGNODB_PASSWORD")

        if not self.uri:
            raise RuntimeError("COGNODB_URI is missing from .env")

        if not self.username:
            raise RuntimeError("COGNODB_USERNAME is missing from .env")

        if not self.password:
            raise RuntimeError("COGNODB_PASSWORD is missing from .env")

        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )

        self.driver.verify_connectivity()

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def clear_database(self):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n)
                DETACH DELETE n
                """
            ).consume()

    def load_data(self, nodes, relationships):
        raise NotImplementedError(
            "Data loading is handled by scripts/load_cognodb.py."
        )

    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query and return all records.

        Returning the records ensures that benchmark timing includes
        query execution and result retrieval.
        """

        if self.driver is None:
            raise RuntimeError("CognoDB adapter is not connected.")

        parameters = parameters or {}

        with self.driver.session() as session:
            result = session.run(
                query,
                **parameters,
            )

            records = result.data()

            return records

    def point_lookup(self, node_id):
        return self.execute_query(
            """
            MATCH (n {id: $node_id})
            RETURN n
            """,
            {"node_id": node_id},
        )

    def one_hop_traversal(self, node_id):
        return self.execute_query(
            """
            MATCH (a {id: $node_id})-[r]-(b)
            RETURN a, r, b
            """,
            {"node_id": node_id},
        )

    def two_hop_traversal(self, node_id):
        return self.execute_query(
            """
            MATCH (a {id: $node_id})-[r1]-(b)-[r2]-(c)
            RETURN a, r1, b, r2, c
            """,
            {"node_id": node_id},
        )

    def aggregation(self):
        records = self.execute_query(
            """
            MATCH (n)
            RETURN count(n) AS node_count
            """
        )

        if not records:
            return 0

        return records[0]["node_count"]