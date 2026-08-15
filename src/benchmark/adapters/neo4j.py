import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from .base import GraphDatabaseAdapter


class Neo4jAdapter(GraphDatabaseAdapter):
    """
    Neo4j Aura adapter for the benchmark framework.
    """

    def __init__(self):
        load_dotenv()

        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")

        if not self.uri:
            raise RuntimeError("NEO4J_URI is missing from .env")

        if not self.username:
            raise RuntimeError("NEO4J_USERNAME is missing from .env")

        if not self.password:
            raise RuntimeError("NEO4J_PASSWORD is missing from .env")

        self.driver = None

    # -----------------------------------------------------
    # Connection
    # -----------------------------------------------------

    def connect(self):
        """Connect to Neo4j Aura."""

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )

        self.driver.verify_connectivity()

    def close(self):
        """Close the Neo4j connection."""

        if self.driver is not None:
            self.driver.close()
            self.driver = None

    # -----------------------------------------------------
    # Database Management
    # -----------------------------------------------------

    def clear_database(self):
        """Remove all nodes and relationships."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:
            session.run(
                """
                MATCH (n)
                DETACH DELETE n
                """
            ).consume()

    def load_data(self, nodes, relationships):
        """
        Load benchmark nodes and relationships.

        Expected node format:
            {
                "id": "...",
                "label": "...",
                ...
            }

        Expected relationship format:
            {
                "source": "...",
                "target": "...",
                "type": "..."
            }
        """

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:

            # Load nodes
            for node in nodes:

                label = node.get("label", "Node")

                properties = {
                    key: value
                    for key, value in node.items()
                    if key != "label"
                }

                query = f"""
                MERGE (n:{label} {{id: $id}})
                SET n += $properties
                """

                session.run(
                    query,
                    id=properties.get("id"),
                    properties=properties,
                ).consume()

            # Load relationships
            for relationship in relationships:

                source = relationship["source"]
                target = relationship["target"]
                rel_type = relationship.get(
                    "type",
                    "RELATED_TO",
                )

                query = f"""
                MATCH (a {{id: $source}})
                MATCH (b {{id: $target}})
                MERGE (a)-[r:{rel_type}]->(b)
                """

                session.run(
                    query,
                    source=source,
                    target=target,
                ).consume()


    # -----------------------------------------------------
    # Verification
    # -----------------------------------------------------

    def get_node_count(self):
        """Return the total number of nodes."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                RETURN count(n) AS count
                """
            ).single()

            return result["count"]

    def get_relationship_count(self):
        """Return the total number of relationships."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH ()-[r]->()
                RETURN count(r) AS count
                """
            ).single()

            return result["count"]

    # -----------------------------------------------------
    # Generic Query Execution
    # -----------------------------------------------------

    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query and return materialized records.
        """

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        if parameters is None:
            parameters = {}

        with self.driver.session() as session:

            result = session.run(
                query,
                parameters,
            )

            return list(result)

    # -----------------------------------------------------
    # Benchmark Workloads
    # -----------------------------------------------------

    def point_lookup(self, node_id):
        """Execute a point lookup query."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (n {id: $node_id})
                RETURN n
                """,
                node_id=node_id,
            )

            return list(result)

    def one_hop_traversal(self, node_id):
        """Execute a 1-hop traversal."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (n {id: $node_id})-->(m)
                RETURN m
                """,
                node_id=node_id,
            )

            return list(result)

    def two_hop_traversal(self, node_id):
        """Execute a 2-hop traversal."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (n {id: $node_id})
                      -[*1..2]->(m)
                RETURN DISTINCT m
                """,
                node_id=node_id,
            )

            return list(result)

    def aggregation(self):
        """Execute an aggregation workload."""

        if self.driver is None:
            raise RuntimeError("Database is not connected.")

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (n)
                RETURN labels(n) AS labels,
                       count(n) AS count
                ORDER BY count DESC
                """
            )

            return list(result)