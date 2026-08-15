from src.benchmark.adapters.neo4j import Neo4jAdapter


def main():
    print("=" * 50)
    print("Neo4j Aura Adapter Test")
    print("=" * 50)

    adapter = Neo4jAdapter()

    try:
        print("Connecting to Neo4j Aura...")

        adapter.connect()

        print("Neo4j Aura connection successful!")

        node_count = adapter.get_node_count()
        relationship_count = adapter.get_relationship_count()

        print()
        print(f"Current node count: {node_count:,}")
        print(
            f"Current relationship count: "
            f"{relationship_count:,}"
        )

    except Exception as error:
        print()
        print("Neo4j connection failed!")
        print(f"Error: {error}")
        raise

    finally:
        adapter.close()
        print()
        print("Neo4j connection closed.")


if __name__ == "__main__":
    main()