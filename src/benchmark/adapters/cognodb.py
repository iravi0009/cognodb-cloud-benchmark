import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from .base import GraphDatabaseAdapter


class CognoDBAdapter(GraphDatabaseAdapter):
    """
    CognoDB Cloud adapter using the official Neo4j Python driver.
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

    def clear_database(self):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n)
                DETACH DELETE n
                """
            )

    def load_data(self, nodes, relationships):
        raise NotImplementedError(
            "Data loading will be implemented in the dataset step."
        )

    def point_lookup(self, node_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n {id: $node_id})
                RETURN n
                """,
                node_id=node_id,
            )
            return result.data()

    def one_hop_traversal(self, node_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a {id: $node_id})-[r]-(b)
                RETURN a, r, b
                """,
                node_id=node_id,
            )
            return result.data()

    def two_hop_traversal(self, node_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a {id: $node_id})-[r1]-(b)-[r2]-(c)
                RETURN a, r1, b, r2, c
                """,
                node_id=node_id,
            )
            return result.data()

    def aggregation(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                RETURN count(n) AS node_count
                """
            )
            return result.single()["node_count"]