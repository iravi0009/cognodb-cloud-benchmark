import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"


EXPECTED_COUNTS = {
    "persons.csv": 10_000,
    "companies.csv": 1_000,
    "technologies.csv": 100,
    "works_at.csv": 10_000,
    "knows.csv": 50_000,
    "person_uses.csv": 20_000,
    "company_uses.csv": 5_000,
}


def count_rows(path):
    with path.open("r", encoding="utf-8", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


def validate_file(filename, expected):
    path = DATA_DIR / filename

    if not path.exists():
        print(f"[FAIL] Missing file: {filename}")
        return False

    actual = count_rows(path)

    if actual != expected:
        print(
            f"[FAIL] {filename}: "
            f"expected {expected:,}, found {actual:,}"
        )
        return False

    print(f"[PASS] {filename}: {actual:,} records")
    return True


def main():
    print("=" * 60)
    print("CognoDB Benchmark Dataset Validation")
    print("=" * 60)
    print()

    all_valid = True

    for filename, expected in EXPECTED_COUNTS.items():
        if not validate_file(filename, expected):
            all_valid = False

    print()

    if all_valid:
        print("Dataset validation successful.")
        print("All expected files and record counts are correct.")
    else:
        print("Dataset validation FAILED.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()