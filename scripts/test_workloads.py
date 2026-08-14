import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase

from src.benchmark.workloads.queries import WORKLOADS


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


def main():

    print("=" * 60)
    print("CognoDB Benchmark Workload Test")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        print("CognoDB connection successful!")
        print()

        with driver.session() as session:

            for workload in WORKLOADS:

                print(
                    f"Running: {workload.name}"
                )

                start = time.perf_counter()

                result = session.run(
                    workload.query,
                    workload.parameters,
                )

                records = list(result)

                elapsed = (
                    time.perf_counter() - start
                )

                print(
                    f"  Description: "
                    f"{workload.description}"
                )

                print(
                    f"  Records: "
                    f"{len(records)}"
                )

                print(
                    f"  Latency: "
                    f"{elapsed * 1000:.3f} ms"
                )

                print()

    finally:

        driver.close()

    print("=" * 60)
    print("Workload test completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()