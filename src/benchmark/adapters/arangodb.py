import os

from arango import ArangoClient
from dotenv import load_dotenv


class ArangoDBAdapter:
    """ArangoDB adapter for the Wiki-Vote benchmark."""

    def __init__(self):
        load_dotenv()

        self.url = os.getenv("ARANGODB_URL")
        self.username = os.getenv("ARANGODB_USERNAME", "root")
        self.password = os.getenv("ARANGODB_PASSWORD")
        self.database_name = os.getenv(
            "ARANGODB_DATABASE",
            "_system",
        )

        self.client = None
        self.db = None

    def connect(self):
        if not self.url:
            raise RuntimeError(
                "ARANGODB_URL is missing from .env"
            )

        if not self.password:
            raise RuntimeError(
                "ARANGODB_PASSWORD is missing from .env"
            )

        print(
            "Connecting to ArangoDB...",
            flush=True,
        )

        self.client = ArangoClient(
            hosts=self.url
        )

        self.db = self.client.db(
            self.database_name,
            username=self.username,
            password=self.password,
        )

        # Verify the connection.
        self.db.version()

        print(
            "ArangoDB connection successful!",
            flush=True,
        )

    def execute_query(self, query, parameters=None):
        """
        Execute an ArangoDB AQL query.

        runner.py already converts the Wiki-Vote workload
        into ArangoDB-compatible AQL, so this adapter must
        NOT translate the query again.
        """

        if self.db is None:
            raise RuntimeError(
                "ArangoDB is not connected"
            )

        bind_vars = dict(parameters or {})

        # Different AQL workloads use user_id differently:
        #
        # 1. _key / CONCAT(..., @user_id)
        #    -> ArangoDB document keys are strings.
        #
        # 2. u.id == @user_id
        #    -> WikiUser.id was loaded as an integer.
        #
        # Therefore, preserve the correct type for each query.

        normalized_query = " ".join(
            query.strip().split()
        )

        if "u.id == @user_id" in normalized_query:
            if "user_id" in bind_vars:
                bind_vars["user_id"] = int(
                    bind_vars["user_id"]
                )

        elif "user_id" in bind_vars:
            bind_vars["user_id"] = str(
                bind_vars["user_id"]
            )

        cursor = self.db.aql.execute(
            query,
            bind_vars=bind_vars,
            stream=False,
        )

        return list(cursor)

    def close(self):
        self.db = None
        self.client = None