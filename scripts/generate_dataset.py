import csv
import random
from pathlib import Path


SEED = 42

NUM_PERSONS = 10_000
NUM_COMPANIES = 1_000
NUM_TECHNOLOGIES = 100

NUM_KNOWS = 50_000
NUM_PERSON_USES = 20_000
NUM_COMPANY_USES = 5_000


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "generated"


CITIES = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Jaipur",
    "Lucknow",
    "Ahmedabad",
]

ROLES = [
    "Software Engineer",
    "Backend Developer",
    "Data Analyst",
    "Data Scientist",
    "AI Engineer",
    "DevOps Engineer",
    "Product Manager",
    "Business Analyst",
]

INDUSTRIES = [
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Retail",
    "Automotive",
    "Telecommunications",
    "Manufacturing",
]

TECH_CATEGORIES = [
    "Programming Language",
    "Database",
    "Framework",
    "Cloud",
    "DevOps",
    "AI/ML",
]


def write_csv(filename, fieldnames, rows):
    path = OUTPUT_DIR / filename

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {filename}: {len(rows):,} records")


def generate_persons(rng):
    rows = []

    for i in range(1, NUM_PERSONS + 1):
        rows.append(
            {
                "id": f"P{i:06d}",
                "name": f"Person_{i:06d}",
                "age": rng.randint(18, 65),
                "city": rng.choice(CITIES),
                "role": rng.choice(ROLES),
            }
        )

    return rows


def generate_companies(rng):
    rows = []

    for i in range(1, NUM_COMPANIES + 1):
        rows.append(
            {
                "id": f"C{i:06d}",
                "name": f"Company_{i:06d}",
                "industry": rng.choice(INDUSTRIES),
                "size": rng.randint(10, 10_000),
            }
        )

    return rows


def generate_technologies():
    technologies = [
        "Python",
        "C++",
        "Java",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "SQL",
        "React",
        "Next.js",
        "FastAPI",
        "Flask",
        "Django",
        "Node.js",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "Git",
        "Linux",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "Neo4j",
        "GraphQL",
        "REST",
        "Kafka",
        "Spark",
        "Airflow",
        "Jenkins",
        "Terraform",
        "Ansible",
        "OpenAI",
    ]

    rows = []

    for i in range(1, NUM_TECHNOLOGIES + 1):
        name = technologies[(i - 1) % len(technologies)]

        rows.append(
            {
                "id": f"T{i:06d}",
                "name": name,
                "category": TECH_CATEGORIES[
                    (i - 1) % len(TECH_CATEGORIES)
                ],
            }
        )

    return rows


def generate_works_at(rng):
    rows = []

    for person_id in range(1, NUM_PERSONS + 1):
        company_id = rng.randint(1, NUM_COMPANIES)

        rows.append(
            {
                "person_id": f"P{person_id:06d}",
                "company_id": f"C{company_id:06d}",
                "since": rng.randint(2015, 2026),
                "position": rng.choice(ROLES),
            }
        )

    return rows


def generate_knows(rng):
    rows = []
    pairs = set()

    while len(rows) < NUM_KNOWS:
        person_a = rng.randint(1, NUM_PERSONS)
        person_b = rng.randint(1, NUM_PERSONS)

        if person_a == person_b:
            continue

        pair = tuple(sorted((person_a, person_b)))

        if pair in pairs:
            continue

        pairs.add(pair)

        rows.append(
            {
                "person_a": f"P{person_a:06d}",
                "person_b": f"P{person_b:06d}",
                "since": rng.randint(2015, 2026),
                "strength": rng.randint(1, 100),
            }
        )

    return rows


def generate_person_uses(rng):
    rows = []
    pairs = set()

    while len(rows) < NUM_PERSON_USES:
        person_id = rng.randint(1, NUM_PERSONS)
        technology_id = rng.randint(1, NUM_TECHNOLOGIES)

        pair = (person_id, technology_id)

        if pair in pairs:
            continue

        pairs.add(pair)

        rows.append(
            {
                "person_id": f"P{person_id:06d}",
                "technology_id": f"T{technology_id:06d}",
                "years": rng.randint(1, 10),
                "proficiency": rng.randint(1, 100),
            }
        )

    return rows


def generate_company_uses(rng):
    rows = []
    pairs = set()

    while len(rows) < NUM_COMPANY_USES:
        company_id = rng.randint(1, NUM_COMPANIES)
        technology_id = rng.randint(1, NUM_TECHNOLOGIES)

        pair = (company_id, technology_id)

        if pair in pairs:
            continue

        pairs.add(pair)

        rows.append(
            {
                "company_id": f"C{company_id:06d}",
                "technology_id": f"T{technology_id:06d}",
                "years": rng.randint(1, 10),
                "proficiency": rng.randint(1, 100),
            }
        )

    return rows


def main():
    rng = random.Random(SEED)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating deterministic benchmark dataset...")
    print(f"Random seed: {SEED}")
    print()

    persons = generate_persons(rng)
    companies = generate_companies(rng)
    technologies = generate_technologies()
    works_at = generate_works_at(rng)
    knows = generate_knows(rng)
    person_uses = generate_person_uses(rng)
    company_uses = generate_company_uses(rng)

    write_csv(
        "persons.csv",
        ["id", "name", "age", "city", "role"],
        persons,
    )

    write_csv(
        "companies.csv",
        ["id", "name", "industry", "size"],
        companies,
    )

    write_csv(
        "technologies.csv",
        ["id", "name", "category"],
        technologies,
    )

    write_csv(
        "works_at.csv",
        ["person_id", "company_id", "since", "position"],
        works_at,
    )

    write_csv(
        "knows.csv",
        ["person_a", "person_b", "since", "strength"],
        knows,
    )

    write_csv(
        "person_uses.csv",
        ["person_id", "technology_id", "years", "proficiency"],
        person_uses,
    )

    write_csv(
        "company_uses.csv",
        ["company_id", "technology_id", "years", "proficiency"],
        company_uses,
    )

    print()
    print("Dataset generation completed successfully.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()