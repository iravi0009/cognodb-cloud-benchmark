import argparse


SUPPORTED_DATABASES = [
    "cognodb",
    "neo4j",
    "memgraph",
    "falkordb",
    "arangodb",
]


def main():
    parser = argparse.ArgumentParser(
        description="CognoDB Cloud Graph Database Benchmark"
    )

    parser.add_argument(
        "--database",
        required=True,
        choices=SUPPORTED_DATABASES,
        help="Database to benchmark",
    )

    args = parser.parse_args()

    print("========================================")
    print("CognoDB Cloud Graph Database Benchmark")
    print("========================================")
    print(f"Selected database: {args.database}")
    print()
    print("Benchmark runner initialized successfully.")
    print("Database adapter implementation will be added next.")


if __name__ == "__main__":
    main()