\# CognoDB Cloud Graph Database Benchmark



A reproducible benchmarking framework for evaluating the performance of a cloud-hosted graph database using a synthetic graph dataset, representative graph-query workloads, automated latency measurement, and result analysis.



\---



\## 📌 Project Overview



This project provides a complete benchmark pipeline for evaluating graph database query performance.



The system generates a synthetic graph dataset, validates the generated data, loads the dataset into CognoDB Cloud, executes representative graph workloads, measures query latency, and generates statistical summaries and performance visualizations.



The benchmark is designed to be:



\- Reproducible

\- Modular

\- Extensible

\- Dataset-driven

\- Workload-driven

\- Suitable for cross-database comparison



The project currently contains a working CognoDB adapter and benchmark implementation.



\---



\## 🎯 Objectives



The main objectives of this project are:



1\. Build a reproducible graph database benchmarking framework.

2\. Generate a controlled synthetic graph dataset.

3\. Load large-scale graph data into CognoDB Cloud.

4\. Execute representative graph queries.

5\. Measure query latency and reliability.

6\. Calculate aggregate performance statistics.

7\. Generate workload-level performance reports.

8\. Produce charts for latency analysis.

9\. Provide a foundation for future cross-database benchmarking.



\---



\## 🏗️ Benchmark Architecture



```text

\&#x20;                   ┌──────────────────────┐

\&#x20;                   │  Synthetic Dataset   │

\&#x20;                   │     Generator        │

\&#x20;                   └──────────┬───────────┘

\&#x20;                              │

\&#x20;                              ▼

\&#x20;                   ┌──────────────────────┐

\&#x20;                   │ Dataset Validation   │

\&#x20;                   └──────────┬───────────┘

\&#x20;                              │

\&#x20;                              ▼

\&#x20;                   ┌──────────────────────┐

\&#x20;                   │    CognoDB Cloud     │

\&#x20;                   │    Graph Database    │

\&#x20;                   └──────────┬───────────┘

\&#x20;                              │

\&#x20;            ┌─────────────────┼─────────────────┐

\&#x20;            │                 │                 │

\&#x20;            ▼                 ▼                 ▼

\&#x20;       Person Nodes      Company Nodes    Technology Nodes

\&#x20;            │                 │                 │

\&#x20;            └─────────────────┼─────────────────┘

\&#x20;                              │

\&#x20;                              ▼

\&#x20;                   ┌──────────────────────┐

\&#x20;                   │ Benchmark Workloads  │

\&#x20;                   └──────────┬───────────┘

\&#x20;                              │

\&#x20;                              ▼

\&#x20;                   ┌──────────────────────┐

\&#x20;                   │ Latency Measurement  │

\&#x20;                   └──────────┬───────────┘

\&#x20;                              │

\&#x20;                 ┌────────────┼────────────┐

\&#x20;                 │            │            │

\&#x20;                 ▼            ▼            ▼

\&#x20;            Raw Results   Statistics    Charts





📊 Dataset



The benchmark uses a synthetic graph dataset containing people, companies, technologies, and relationships between them.



Dataset Statistics

Entity / Relationship	Records

Persons	10,000

Companies	1,000

Technologies	100

WORKS\\\_AT relationships	10,000

KNOWS relationships	50,000

Person USES Technology	20,000

Company USES Technology	5,000

Total Nodes	11,100

Total Relationships	85,000

Graph Model

Person ────── WORKS\\\_AT ──────> Company





Person ────── KNOWS ──────────> Person





Person ────── USES ───────────> Technology





Company ───── USES ───────────> Technology

📁 Dataset Files



The generated dataset contains seven CSV files:



data/

└── generated/

\&#x20;   ├── persons.csv

\&#x20;   ├── companies.csv

\&#x20;   ├── technologies.csv

\&#x20;   ├── works\\\_at.csv

\&#x20;   ├── knows.csv

\&#x20;   ├── person\\\_uses.csv

\&#x20;   └── company\\\_uses.csv

Dataset Record Counts

persons.csv          10,000 records

companies.csv         1,000 records

technologies.csv        100 records

works\\\_at.csv         10,000 records

knows.csv            50,000 records

person\\\_uses.csv      20,000 records

company\\\_uses.csv      5,000 records



The dataset is generated locally using the project dataset-generation script.



Generated datasets are excluded from Git to keep the repository lightweight and reproducible.



🧪 Benchmark Methodology



The benchmark follows a controlled execution pipeline.



Generate Dataset

\&#x20;      ↓

Validate Dataset

\&#x20;      ↓

Load Dataset

\&#x20;      ↓

Verify Database

\&#x20;      ↓

Execute Warm-up

\&#x20;      ↓

Execute Benchmark Runs

\&#x20;      ↓

Collect Latency

\&#x20;      ↓

Save Raw Results

\&#x20;      ↓

Analyze Results

\&#x20;      ↓

Generate Charts



For each workload, the benchmark records:



Workload name

Database name

Description

Run number

Execution status

Query latency

Returned record count

Error information when applicable

🔍 Benchmark Workloads



The current benchmark contains 10 workloads.



Workload	Description

person\\\_lookup	Look up a person by ID

company\\\_lookup	Look up a company by ID

technology\\\_lookup	Look up a technology by ID

person\\\_company	Find the company where a person works

person\\\_connections	Find people directly connected to a person

person\\\_technologies	Find technologies used by a person

company\\\_technologies	Find technologies used by a company

technology\\\_users	Find people using a technology

two\\\_hop\\\_network	Perform a two-hop KNOWS traversal

company\\\_employee\\\_count	Count employees of a company

🔎 Query Workload Categories



The workloads represent different graph-query patterns.



1\\. Direct Lookup



Examples:



person\\\_lookup

company\\\_lookup

technology\\\_lookup



These workloads test direct node retrieval using identifiers.



2\\. One-Hop Traversal



Examples:



person\\\_company

person\\\_connections

person\\\_technologies

company\\\_technologies

technology\\\_users



These workloads test relationships between directly connected nodes.



3\\. Multi-Hop Traversal

two\\\_hop\\\_network



This workload tests traversal across multiple graph relationships.



4\\. Aggregation

company\\\_employee\\\_count



This workload tests counting related graph entities.



⚡ Benchmark Metrics



The benchmark calculates the following metrics.



Metric	Description

Average latency	Mean execution time

Median latency	Middle execution time

Minimum latency	Fastest execution

Maximum latency	Slowest execution

P95 latency	95th percentile latency

P99 latency	99th percentile latency

Success rate	Percentage of successful executions

Error count	Number of failed executions

Record count	Number of returned records



Latency is measured in milliseconds.



📈 CognoDB Benchmark Results



The current CognoDB benchmark run completed successfully.



Overall Results

Metric	Result

Total measurements	100

Successful measurements	100

Errors	0

Success rate	100%

Average latency	246.41 ms

Median latency	246.01 ms

Minimum latency	244.04 ms

Maximum latency	250.95 ms

P95 latency	249.57 ms

P99 latency	250.74 ms

Result Interpretation



The benchmark produced 100 successful measurements with zero errors.



The observed average latency was approximately:



246.41 ms



The observed P95 latency was approximately:



249.57 ms



The fastest recorded execution was approximately:



244.04 ms



The slowest recorded execution was approximately:



250.95 ms



These results represent the current benchmark execution and should not be interpreted as universal database performance guarantees. Network conditions, database configuration, query parameters, workload characteristics, and infrastructure can influence benchmark results.



📊 Workload-Level Results



The current benchmark produced the following approximate average latency values:



Workload	Measurements	Average Latency

company\\\_lookup	10	245.29 ms

person\\\_lookup	10	245.60 ms

technology\\\_lookup	10	245.87 ms

company\\\_employee\\\_count	10	245.88 ms

company\\\_technologies	10	245.93 ms

person\\\_company	10	246.00 ms

person\\\_technologies	10	246.19 ms

person\\\_connections	10	247.13 ms

technology\\\_users	10	248.06 ms

two\\\_hop\\\_network	10	248.13 ms

Observations



Based on the current benchmark run:



Direct lookup workloads generally showed lower latency.

Relationship traversal workloads showed slightly higher latency.

The two\\\_hop\\\_network workload had the highest average latency.

The company\\\_lookup workload had the lowest average latency.

All workloads completed successfully.

No benchmark errors were recorded.

📉 Benchmark Visualizations



The result-analysis pipeline generates three charts:



results/

└── charts/

\&#x20;   ├── latency\\\_by\\\_workload.png

\&#x20;   ├── latency\\\_distribution.png

\&#x20;   └── workload\\\_comparison.png

Generated Charts

Latency by Workload



Shows the average latency of each benchmark workload.



Latency Distribution



Shows how query execution latency is distributed across benchmark measurements.



Workload Comparison



Provides a visual comparison of workload performance.



📄 Benchmark Output

Raw Results



Raw measurements are saved to:



results/raw/cognodb\\\_benchmark.csv

Processed Results



Workload-level results:



results/processed/cognodb\\\_summary.csv



Overall benchmark results:



results/processed/cognodb\\\_overall.csv

🛠️ Technology Stack

Programming Language

Python 3.13

Database

CognoDB Cloud

Neo4j-compatible Bolt driver

Cypher

Python Libraries

neo4j

python-dotenv

pandas

matplotlib

Development Tools

Git

GitHub

PowerShell

Visual Studio Code / Notepad

📂 Project Structure

cognodb-cloud-benchmark/

│

├── data/

│   └── generated/

│

├── docs/

│

├── results/

│   ├── raw/

│   ├── processed/

│   └── charts/

│

├── scripts/

│   ├── analyze\\\_results.py

│   ├── check\\\_tls.py

│   ├── generate\\\_dataset.py

│   ├── load\\\_cognodb.py

│   ├── test\\\_adapter.py

│   ├── test\\\_cognodb.py

│   ├── test\\\_cognodb\\\_tls.py

│   ├── test\\\_workloads.py

│   └── validate\\\_dataset.py

│

├── src/

│   └── benchmark/

│       │

│       ├── adapters/

│       │   ├── base.py

│       │   ├── cognodb.py

│       │   └── \\\_\\\_init\\\_\\\_.py

│       │

│       ├── workloads/

│       │   ├── queries.py

│       │   └── \\\_\\\_init\\\_\\\_.py

│       │

│       ├── runner.py

│       └── \\\_\\\_init\\\_\\\_.py

│

├── .env.example

├── .gitignore

├── README.md

└── requirements.txt

⚙️ Installation

1\\. Clone the Repository

git clone https://github.com/iravi0009/cognodb-cloud-benchmark.git



Move into the project directory:



cd cognodb-cloud-benchmark

2\\. Create a Python Virtual Environment

Windows PowerShell

python -m venv .venv



Activate it:



.venv\\\\Scripts\\\\Activate.ps1

3\\. Install Dependencies

pip install -r requirements.txt

🔐 Environment Configuration



Create a local .env file.



You can copy the example file:



Copy-Item .env.example .env



Then configure your CognoDB credentials:



COGNODB\\\_URI=bolt+s://your-cognodb-host

COGNODB\\\_USERNAME=your\\\_username

COGNODB\\\_PASSWORD=your\\\_password



Do not commit .env to Git.



The .gitignore configuration excludes the .env file.



🗃️ Generate the Dataset



Run:



python scripts/generate\\\_dataset.py



The generator creates:



10,000 persons

1,000 companies

100 technologies

10,000 works\\\_at relationships

50,000 knows relationships

20,000 person\\\_uses relationships

5,000 company\\\_uses relationships

✅ Validate the Dataset



Run:



python scripts/validate\\\_dataset.py



Expected output:



CognoDB Benchmark Dataset Validation





\\\[PASS] persons.csv: 10,000 records

\\\[PASS] companies.csv: 1,000 records

\\\[PASS] technologies.csv: 100 records

\\\[PASS] works\\\_at.csv: 10,000 records

\\\[PASS] knows.csv: 50,000 records

\\\[PASS] person\\\_uses.csv: 20,000 records

\\\[PASS] company\\\_uses.csv: 5,000 records





Dataset validation successful.

All expected files and record counts are correct.

📥 Load Dataset into CognoDB



Run:



python scripts/load\\\_cognodb.py



The loader creates:



Nodes

Person

Company

Technology

Relationships

WORKS\\\_AT

KNOWS

USES



The loader also creates indexes for:



Person.id

Company.id

Technology.id



After loading, the current database contains:



Total nodes: 11,100

Total relationships: 85,000

🧪 Test CognoDB Adapter



Run:



python -m scripts.test\\\_adapter



Expected output:



CognoDB adapter connection successful!

Current node count: 11,100

🏃 Run Benchmark Workloads



Run the workload test:



python scripts/test\\\_workloads.py



Alternatively, run the benchmark runner:



python -m src.benchmark.runner --database cognodb



The benchmark runner:



Connects to CognoDB.

Loads the configured workloads.

Performs warm-up execution.

Executes measured runs.

Records latency.

Records returned records.

Tracks errors.

Saves raw benchmark results.

📊 Analyze Benchmark Results



Run:



python scripts/analyze\\\_results.py



The analysis script reads:



results/raw/cognodb\\\_benchmark.csv



and generates:



results/processed/cognodb\\\_summary.csv

results/processed/cognodb\\\_overall.csv



and charts:



results/charts/latency\\\_by\\\_workload.png

results/charts/latency\\\_distribution.png

results/charts/workload\\\_comparison.png

🔄 Complete Benchmark Workflow



The complete workflow can be executed in the following order:



python scripts/generate\\\_dataset.py

python scripts/validate\\\_dataset.py

python scripts/load\\\_cognodb.py

python scripts/test\\\_workloads.py

python scripts/analyze\\\_results.py

🔒 Security



Database credentials are stored in environment variables.



Example:



COGNODB\\\_URI=...

COGNODB\\\_USERNAME=...

COGNODB\\\_PASSWORD=...



Credentials should never be committed to Git.



The repository ignores:



.env

.venv/



and generated benchmark data/results.



♻️ Reproducibility



The project is designed around a reproducible benchmark workflow.



Dataset Generation

\&#x20;       ↓

Dataset Validation

\&#x20;       ↓

Database Loading

\&#x20;       ↓

Database Verification

\&#x20;       ↓

Benchmark Execution

\&#x20;       ↓

Raw Result Storage

\&#x20;       ↓

Statistical Analysis

\&#x20;       ↓

Visualization



Because the dataset is generated programmatically, the benchmark can be repeated with the same dataset-generation configuration.



🌐 GitHub Repository



Source code:



https://github.com/iravi0009/cognodb-cloud-benchmark



🚧 Future Improvements



The framework is designed to support additional databases and workloads.



Planned improvements include:



Neo4j Cloud adapter

Memgraph adapter

FalkorDB adapter

ArangoDB adapter

Cross-database comparison

Concurrent query execution

Larger datasets

Configurable benchmark sizes

Throughput measurement

Connection-pool benchmarking

Query-plan analysis

Automated performance regression detection

CI/CD benchmark execution

Historical benchmark comparison

Automated benchmark reports

📌 Current Project Status

Component	Status

Project setup	✅ Complete

Git repository	✅ Complete

GitHub repository	✅ Complete

CognoDB connection	✅ Complete

CognoDB adapter	✅ Complete

Dataset generation	✅ Complete

Dataset validation	✅ Complete

Dataset loading	✅ Complete

Database verification	✅ Complete

Benchmark workloads	✅ Complete

Benchmark execution	✅ Complete

Raw result generation	✅ Complete

Result analysis	✅ Complete

Chart generation	✅ Complete

Cross-database comparison	🚧 Planned



📜 License



This project is intended for benchmarking, experimentation, research, and educational purposes.







\\---





\\## 4. Save the file





After pasting everything:





\\\*\\\*Press `Ctrl + S`\\\*\\\*





Then close Notepad.





\\---





\\## 5. Verify the README





Back in PowerShell, run:





```powershell

Get-Content README.md








