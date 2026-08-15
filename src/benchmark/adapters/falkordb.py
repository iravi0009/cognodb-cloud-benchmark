import os

from dotenv import load_dotenv
import redis


class FalkorDBAdapter:

    def __init__(self):
        load_dotenv()

        self.host = os.getenv("FALKORDB_HOST")
        self.port = int(os.getenv("FALKORDB_PORT", "6379"))
        self.username = os.getenv("FALKORDB_USERNAME")
        self.password = os.getenv("FALKORDB_PASSWORD")
        self.ssl = os.getenv("FALKORDB_TLS", "false").lower() == "true"

        self.client = None
        self.graph_name = "wikivote"

    def connect(self):
        print("Connecting directly to FalkorDB...", flush=True)

        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            ssl=self.ssl,
            socket_connect_timeout=10,
            socket_timeout=30,
            decode_responses=True,
        )

        print("Redis client created.", flush=True)

        self.client.ping()

        print("FalkorDB PING successful.", flush=True)

    def execute_query(self, query, parameters=None):
        if self.client is None:
            raise RuntimeError("FalkorDB is not connected")

        result = self.client.execute_command(
            "GRAPH.QUERY",
            self.graph_name,
            query,
        )

        if not result:
            return []

        if len(result) >= 2 and isinstance(result[1], list):
            return result[1]

        return []

    def close(self):
        if self.client is not None:
            self.client.close()

        self.client = None