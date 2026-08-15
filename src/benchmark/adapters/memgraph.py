import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


class MemgraphAdapter:

    def __init__(self):
        load_dotenv()

        self.uri = os.getenv("MEMGRAPH_URI")
        self.username = os.getenv("MEMGRAPH_USERNAME")
        self.password = os.getenv("MEMGRAPH_PASSWORD")

        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )

        self.driver.verify_connectivity()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {},
            )

            return [record.data() for record in result]

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None