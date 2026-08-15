import csv
from pathlib import Path

source = Path("data/wiki-Vote/wiki-Vote.mtx")
output = Path("data/wiki-vote-edges.csv")

with source.open("r", encoding="utf-8") as f, output.open(
    "w", newline="", encoding="utf-8"
) as out:
    writer = csv.writer(out)
    writer.writerow(["source", "target"])

    for line in f:
        line = line.strip()

        if not line or line.startswith("%"):
            continue

        parts = line.split()

        # Skip Matrix Market size line
        if len(parts) == 3:
            continue

        if len(parts) >= 2:
            writer.writerow([parts[0], parts[1]])

print(f"Created: {output}")