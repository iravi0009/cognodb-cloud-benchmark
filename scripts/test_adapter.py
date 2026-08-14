from src.benchmark.adapters.cognodb import CognoDBAdapter


def main():
    adapter = CognoDBAdapter()

    try:
        adapter.connect()

        print("CognoDB adapter connection successful!")

        count = adapter.aggregation()
        print(f"Current node count: {count}")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()