@'

\# CognoDB Cloud Graph Database Benchmark



A reproducible benchmarking framework for evaluating cloud-hosted graph database performance using a synthetic graph dataset, representative graph-query workloads, automated latency measurement, statistical analysis, and performance visualization.



\---



\## 📌 Project Overview



This project provides a complete benchmark pipeline for evaluating graph database query performance.



The framework:



1\. Generates a synthetic graph dataset.

2\. Validates the generated dataset.

3\. Loads the dataset into CognoDB Cloud.

4\. Verifies the loaded graph.

5\. Executes representative graph-query workloads.

6\. Measures query latency.

7\. Stores raw benchmark measurements.

8\. Calculates statistical performance metrics.

9\. Generates workload-level summaries.

10\. Generates performance visualization charts.



The project is designed to be:



\- Reproducible

\- Modular

\- Dataset-driven

\- Workload-driven

\- Extensible

\- Suitable for future cross-database benchmarking



The current implementation includes a working CognoDB adapter and a complete benchmark execution and analysis pipeline.



\---



\## 🎯 Objectives



The main objectives of this project are:



1\. Build a reproducible graph database benchmarking framework.

2\. Generate a controlled synthetic graph dataset.

3\. Load large-scale graph data into a cloud-hosted graph database.

4\. Execute representative graph queries.

5\. Measure query latency and execution reliability.

6\. Calculate aggregate performance statistics.

7\. Generate workload-level benchmark reports.

8\. Generate latency visualization charts.

9\. Provide an extensible architecture for additional graph databases.

10\. Establish a foundation for future cross-database performance comparison.



\---



\## 🏗️ Benchmark Architecture



```text

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Synthetic Dataset      │

&#x20;                 │ Generator              │

&#x20;                 │ generate\_dataset.py    │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Dataset Validation     │

&#x20;                 │ validate\_dataset.py    │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Database Loader         │

&#x20;                 │ load\_cognodb.py        │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ CognoDB Cloud           │

&#x20;                 │ Graph Database          │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Database Verification   │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Benchmark Workloads     │

&#x20;                 │ queries.py              │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Benchmark Runner        │

&#x20;                 │ runner.py              │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Latency Measurement     │

&#x20;                 └───────────┬────────────┘

&#x20;                             │

&#x20;               ┌─────────────┼─────────────┐

&#x20;               ▼             ▼             ▼

&#x20;         Raw Results     Statistics      Charts

&#x20;               │             │             │

&#x20;               └─────────────┼─────────────┘

&#x20;                             ▼

&#x20;                 ┌────────────────────────┐

&#x20;                 │ Result Analysis         │

&#x20;                 │ analyze\_results.py      │

&#x20;                 └────────────────────────┘



````



\---



\## 🗃️ Dataset



The benchmark uses a synthetic graph dataset representing people, companies, technologies, and relationships between them.



\### Dataset Statistics



| Entity / RelationshipRecords |            |

| ---------------------------- | ---------- |

| Persons                      | 10,000     |

| Companies                    | 1,000      |

| Technologies                 | 100        |

| `WORKS\_AT` relationships     | 10,000     |

| `KNOWS` relationships        | 50,000     |

| Person `USES` Technology     | 20,000     |

| Company `USES` Technology    | 5,000      |

| \*\*Total Nodes\*\*              | \*\*11,100\*\* |

| \*\*Total Relationships\*\*      | \*\*85,000\*\* |



\### Graph Model



```

Person ────── WORKS\_AT ──────> Company



Person ────── KNOWS ──────────> Person



Person ────── USES ───────────> Technology



Company ───── USES ───────────> Technology



```



The dataset is generated locally using the project dataset-generation script.



Generated datasets are excluded from Git where appropriate to keep the repository lightweight and reproducible.



\---



\## 📁 Dataset Files



The generated dataset contains seven CSV files:



```

data/

└── generated/

&#x20;   ├── persons.csv

&#x20;   ├── companies.csv

&#x20;   ├── technologies.csv

&#x20;   ├── works\_at.csv

&#x20;   ├── knows.csv

&#x20;   ├── person\_uses.csv

&#x20;   └── company\_uses.csv



```



\### Dataset Record Counts



| FileRecordsDescription |        |                                     |

| ---------------------- | ------ | ----------------------------------- |

| `persons.csv`          | 10,000 | Person nodes                        |

| `companies.csv`        | 1,000  | Company nodes                       |

| `technologies.csv`     | 100    | Technology nodes                    |

| `works\_at.csv`         | 10,000 | Person-to-company relationships     |

| `knows.csv`            | 50,000 | Person-to-person relationships      |

| `person\_uses.csv`      | 20,000 | Person-to-technology relationships  |

| `company\_uses.csv`     | 5,000  | Company-to-technology relationships |



\---



\## 🧪 Benchmark Methodology



The benchmark follows a controlled execution pipeline.



```

Generate Dataset

&#x20;      ↓

Validate Dataset

&#x20;      ↓

Load Dataset

&#x20;      ↓

Verify Database

&#x20;      ↓

Execute Warm-up

&#x20;      ↓

Execute Benchmark Runs

&#x20;      ↓

Collect Latency

&#x20;      ↓

Save Raw Results

&#x20;      ↓

Analyze Results

&#x20;      ↓

Generate Charts



```



For each benchmark measurement, the framework records:



\- Workload name

\- Database name

\- Workload description

\- Run number

\- Execution status

\- Query latency

\- Returned record count

\- Error information when applicable



\### Current Execution Configuration



The current benchmark uses:



\- 10 workloads

\- 1 warm-up run per workload

\- 2 measured runs per workload

\- 10 measurements per workload

\- 100 total measurements

\- CognoDB Cloud as the active database



\---



\## 🔍 Benchmark Workloads



The current benchmark contains 10 graph-query workloads.



| WorkloadDescriptionQuery Pattern |                                            |                     |

| -------------------------------- | ------------------------------------------ | ------------------- |

| `person\_lookup`                  | Look up a person by ID                     | Direct lookup       |

| `company\_lookup`                 | Look up a company by ID                    | Direct lookup       |

| `technology\_lookup`              | Look up a technology by ID                 | Direct lookup       |

| `person\_company`                 | Find the company where a person works      | One-hop traversal   |

| `person\_connections`             | Find people directly connected to a person | One-hop traversal   |

| `person\_technologies`            | Find technologies used by a person         | One-hop traversal   |

| `company\_technologies`           | Find technologies used by a company        | One-hop traversal   |

| `technology\_users`               | Find people using a technology             | One-hop traversal   |

| `two\_hop\_network`                | Perform a two-hop `KNOWS` traversal        | Multi-hop traversal |

| `company\_employee\_count`         | Count employees of a company               | Aggregation         |



\---



\## 🔎 Query Workload Categories



The workloads represent several common graph-query patterns.



\### 1. Direct Lookup



Examples:



```

person\_lookup

company\_lookup

technology\_lookup



```



These workloads test direct node retrieval using identifiers.



\### 2. One-Hop Traversal



Examples:



```

person\_company

person\_connections

person\_technologies

company\_technologies

technology\_users



```



These workloads test relationships between directly connected graph entities.



\### 3. Multi-Hop Traversal



```

two\_hop\_network



```



This workload tests traversal across multiple `KNOWS` relationships.



\### 4. Aggregation



```

company\_employee\_count



```



This workload tests counting related graph entities.



\---



\## ⚡ Benchmark Metrics



The benchmark calculates the following metrics:



| MetricDescription |                                     |

| ----------------- | ----------------------------------- |

| Average latency   | Mean execution time                 |

| Median latency    | Middle execution time               |

| Minimum latency   | Fastest recorded execution          |

| Maximum latency   | Slowest recorded execution          |

| P95 latency       | 95th percentile latency             |

| P99 latency       | 99th percentile latency             |

| Success rate      | Percentage of successful executions |

| Error count       | Number of failed executions         |

| Record count      | Number of returned records          |



Latency is measured in milliseconds.



\---



\## 📈 CognoDB Benchmark Results



The current CognoDB benchmark completed successfully.



\### Overall Results



| MetricResult            |           |

| ----------------------- | --------- |

| Total measurements      | 100       |

| Successful measurements | 100       |

| Errors                  | 0         |

| Success rate            | 100%      |

| Average latency         | 246.41 ms |

| Median latency          | 246.01 ms |

| Minimum latency         | 244.04 ms |

| Maximum latency         | 250.95 ms |

| P95 latency             | 249.57 ms |

| P99 latency             | 250.74 ms |



\### Workload Results



| WorkloadMeasurementsAverage LatencyP95 LatencySuccess Rate |    |           |           |      |

| ---------------------------------------------------------- | -- | --------- | --------- | ---- |

| `company\_lookup`                                           | 10 | 245.28 ms | 247.70 ms | 100% |

| `person\_lookup`                                            | 10 | 245.60 ms | 246.27 ms | 100% |

| `technology\_lookup`                                        | 10 | 245.87 ms | 247.02 ms | 100% |

| `company\_employee\_count`                                   | 10 | 245.88 ms | 247.10 ms | 100% |

| `company\_technologies`                                     | 10 | 245.93 ms | 246.66 ms | 100% |

| `person\_company`                                           | 10 | 246.00 ms | 246.86 ms | 100% |

| `person\_technologies`                                      | 10 | 246.19 ms | 248.22 ms | 100% |

| `person\_connections`                                       | 10 | 247.13 ms | 248.84 ms | 100% |

| `technology\_users`                                         | 10 | 248.06 ms | 250.83 ms | 100% |

| `two\_hop\_network`                                          | 10 | 248.13 ms | 250.74 ms | 100% |



\### Result Interpretation



The current benchmark produced:



\- 100 successful measurements

\- 0 errors

\- 100% success rate

\- Approximately 246.41 ms average latency

\- Approximately 249.57 ms P95 latency



The fastest workload by average latency was:



```

company\_lookup



```



The slowest workload by average latency was:



```

two\_hop\_network



```



The measurements show relatively consistent latency across the tested workloads.



These results represent the current benchmark execution and should not be interpreted as universal CognoDB performance characteristics. Results can vary depending on network conditions, cloud infrastructure, database load, configuration, and execution environment.



\---



\## 📉 Benchmark Visualizations



The result-analysis pipeline generates three charts:



```

results/

└── charts/

&#x20;   ├── latency\_by\_workload.png

&#x20;   ├── latency\_distribution.png

&#x20;   └── workload\_comparison.png



```



\### Latency by Workload



Shows the average latency of each benchmark workload.



\### Latency Distribution



Shows how query execution latency is distributed across benchmark measurements.



\### Workload Comparison



Provides a visual comparison of workload performance.



\---



\## 📄 Benchmark Output



\### Raw Results



Individual benchmark measurements are saved to:



```

results/raw/cognodb\_benchmark.csv



```



The raw result file contains:



\- Timestamp

\- Database

\- Workload

\- Description

\- Run number

\- Status

\- Latency

\- Record count

\- Error information



\### Processed Workload Results



Workload-level statistics are saved to:



```

results/processed/cognodb\_summary.csv



```



\### Overall Benchmark Results



Overall statistics are saved to:



```

results/processed/cognodb\_overall.csv



```



\---



\## 🛠️ Technology Stack



\### Programming Language



```

Python 3.13



```



\### Database



```

CognoDB Cloud



```



\### Database Connectivity



```

Neo4j-compatible Bolt driver

Cypher



```



\### Python Libraries



```

neo4j

python-dotenv

pandas

matplotlib



```



\### Development Tools



```

Git

GitHub

PowerShell

Visual Studio Code

Notepad



```



\---



\## 📂 Project Structure



```

cognodb-cloud-benchmark/

│

├── data/

│   └── generated/

│       ├── persons.csv

│       ├── companies.csv

│       ├── technologies.csv

│       ├── works\_at.csv

│       ├── knows.csv

│       ├── person\_uses.csv

│       └── company\_uses.csv

│

├── docs/

│

├── results/

│   ├── raw/

│   ├── processed/

│   └── charts/

│

├── scripts/

│   ├── analyze\_results.py

│   ├── check\_tls.py

│   ├── generate\_dataset.py

│   ├── load\_cognodb.py

│   ├── test\_adapter.py

│   ├── test\_cognodb.py

│   ├── test\_cognodb\_tls.py

│   ├── test\_workloads.py

│   └── validate\_dataset.py

│

├── src/

│   └── benchmark/

│       ├── adapters/

│       │   ├── base.py

│       │   ├── cognodb.py

│       │   └── \_\_init\_\_.py

│       │

│       ├── workloads/

│       │   ├── queries.py

│       │   └── \_\_init\_\_.py

│       │

│       ├── runner.py

│       └── \_\_init\_\_.py

│

├── .env.example

├── .gitignore

├── README.md

└── requirements.txt



```



\---



\## ⚙️ Installation



\### 1. Clone the Repository



```

git clone https://github.com/iravi0009/cognodb-cloud-benchmark.git



```



\### 2. Move Into the Project Directory



```

cd cognodb-cloud-benchmark



```



\### 3. Create a Python Virtual Environment



Windows PowerShell:



```

python -m venv .venv



```



Activate the environment:



```

.venv\\Scripts\\Activate.ps1



```



\### 4. Install Dependencies



```

pip install -r requirements.txt



```



\---



\## 🔐 Environment Configuration



Create a local `.env` file.



You can copy the example environment file:



```

Copy-Item .env.example .env



```



Configure the required CognoDB credentials:



```

COGNODB\_URI=bolt+s://your-cognodb-host

COGNODB\_USERNAME=your\_username

COGNODB\_PASSWORD=your\_password



```



Do not commit `.env` to Git.



The repository `.gitignore` excludes local credentials and virtual-environment files.



\---



\## 🗃️ Generate the Dataset



Run:



```

python scripts/generate\_dataset.py



```



The generator creates:



```

10,000 persons

1,000 companies

100 technologies

10,000 WORKS\_AT relationships

50,000 KNOWS relationships

20,000 person USES relationships

5,000 company USES relationships



```



\---



\## ✅ Validate the Dataset



Run:



```

python scripts/validate\_dataset.py



```



Expected validation:



```

CognoDB Benchmark Dataset Validation



\[PASS] persons.csv: 10,000 records

\[PASS] companies.csv: 1,000 records

\[PASS] technologies.csv: 100 records

\[PASS] works\_at.csv: 10,000 records

\[PASS] knows.csv: 50,000 records

\[PASS] person\_uses.csv: 20,000 records

\[PASS] company\_uses.csv: 5,000 records



Dataset validation successful.

All expected files and record counts are correct.



```



\---



\## 📥 Load Dataset into CognoDB



Run:



```

python scripts/load\_cognodb.py



```



The loader creates the following node labels:



```

Person

Company

Technology



```



And the following relationship types:



```

WORKS\_AT

KNOWS

USES



```



The loader also creates indexes for:



```

Person.id

Company.id

Technology.id



```



After loading, the verified database contains:



```

Total nodes: 11,100

Total relationships: 85,000



```



\---



\## 🧪 Test the CognoDB Adapter



Run:



```

python -m scripts.test\_adapter



```



Expected output:



```

CognoDB adapter connection successful!

Current node count: 11,100



```



\---



\## 🏃 Run Benchmark Workloads



Run the workload test:



```

python scripts/test\_workloads.py



```



Alternatively, run the benchmark runner:



```

python -m src.benchmark.runner --database cognodb



```



The benchmark runner:



1\. Connects to CognoDB.

2\. Loads the configured workloads.

3\. Performs warm-up execution.

4\. Executes measured runs.

5\. Records query latency.

6\. Records returned records.

7\. Tracks execution errors.

8\. Saves raw benchmark results.



\---



\## 📊 Analyze Benchmark Results



Run:



```

python scripts/analyze\_results.py



```



The analysis script reads:



```

results/raw/cognodb\_benchmark.csv



```



And generates:



```

results/processed/cognodb\_summary.csv

results/processed/cognodb\_overall.csv



```



And performance charts:



```

results/charts/latency\_by\_workload.png

results/charts/latency\_distribution.png

results/charts/workload\_comparison.png



```



\---



\## 🔄 Complete Benchmark Workflow



The complete workflow is:



```

python scripts/generate\_dataset.py



python scripts/validate\_dataset.py



python scripts/load\_cognodb.py



python scripts/test\_workloads.py



python scripts/analyze\_results.py



```



Or execute the benchmark runner directly:



```

python -m src.benchmark.runner --database cognodb



```



\---



\## 🔒 Security



Database credentials are stored using environment variables.



Example:



```

COGNODB\_URI=...

COGNODB\_USERNAME=...

COGNODB\_PASSWORD=...



```



Credentials should never be committed to Git.



The repository excludes sensitive and generated local files such as:



```

.env

.venv/

\_\_pycache\_\_/

\*.pyc



```



Generated benchmark datasets and result artifacts can also be excluded when appropriate.



\---



\## ♻️ Reproducibility



The project is designed around a reproducible benchmark workflow:



```

Dataset Generation

&#x20;      ↓

Dataset Validation

&#x20;      ↓

Database Loading

&#x20;      ↓

Database Verification

&#x20;      ↓

Benchmark Execution

&#x20;      ↓

Raw Result Storage

&#x20;      ↓

Statistical Analysis

&#x20;      ↓

Visualization



```



Because the dataset is generated programmatically and the workloads are explicitly defined, the benchmark can be repeated using the same dataset-generation and benchmark configuration.



Benchmark results can vary between executions because of:



\- Network conditions

\- Cloud infrastructure

\- Database load

\- Connection conditions

\- Query execution environment

\- Resource availability



Therefore, benchmark results should be interpreted as measurements for the tested environment and configuration.



\---



\## 🧩 Adapter Architecture



The project uses a database adapter architecture to separate benchmark logic from database-specific connectivity.



Current architecture:



```

Benchmark Runner

&#x20;      │

&#x20;      ▼

Database Adapter Interface

&#x20;      │

&#x20;      ▼

CognoDB Adapter

&#x20;      │

&#x20;      ▼

CognoDB Cloud



```



The adapter layer is intended to allow additional graph databases to be integrated without rewriting the core benchmark runner and workload definitions.



\### Current Adapter



```

CognoDB



```



\### Planned Adapters



```

Neo4j

Memgraph

FalkorDB

ArangoDB



```



\---



\## 🚧 Future Improvements



The framework is designed to support additional databases, larger datasets, and more advanced benchmark scenarios.



Planned improvements include:



\### Database Support



\- Neo4j Cloud adapter

\- Memgraph adapter

\- FalkorDB adapter

\- ArangoDB adapter

\- Cross-database comparison



\### Benchmark Improvements



\- Larger datasets

\- Configurable dataset sizes

\- Configurable benchmark sizes

\- Concurrent query execution

\- Throughput measurement

\- Connection-pool benchmarking

\- Query-plan analysis

\- More complex traversal workloads



\### Analysis Improvements



\- Automated performance regression detection

\- Historical benchmark comparison

\- Automated benchmark reports

\- Extended statistical analysis

\- Comparative workload dashboards



\### Engineering Improvements



\- CI/CD benchmark execution

\- Automated benchmark pipelines

\- Reproducible benchmark configurations

\- Improved error handling

\- Configurable workload parameters



\---



\## 📌 Current Project Status



| ComponentStatus           |            |

| ------------------------- | ---------- |

| Project setup             | ✅ Complete |

| Git repository            | ✅ Complete |

| GitHub repository         | ✅ Complete |

| CognoDB connection        | ✅ Complete |

| CognoDB adapter           | ✅ Complete |

| Dataset generation        | ✅ Complete |

| Dataset validation        | ✅ Complete |

| Dataset loading           | ✅ Complete |

| Database verification     | ✅ Complete |

| Benchmark workloads       | ✅ Complete |

| Benchmark execution       | ✅ Complete |

| Raw result generation     | ✅ Complete |

| Result analysis           | ✅ Complete |

| Statistical summaries     | ✅ Complete |

| Chart generation          | ✅ Complete |

| README documentation      | ✅ Complete |

| Neo4j adapter             | ✅ Complete |

| Memgraph adapter          | 🚧 Planned |

| FalkorDB adapter          | 🚧 Planned |

| ArangoDB adapter          | 🚧 Planned |

| Cross-database comparison | ✅ Complete |

| Concurrent benchmarking   | 🚧 Planned |



\---



\## 📊 Current Benchmark Snapshot



The current completed CognoDB benchmark demonstrates:



```

Database:

CognoDB Cloud



Dataset:

11,100 nodes

85,000 relationships



Workloads:

10



Measurements:

100



Successful:

100



Errors:

0



Success Rate:

100%



Average Latency:

246.41 ms



P95 Latency:

249.57 ms



Minimum Latency:

244.04 ms



Maximum Latency:

250.95 ms



```



These values represent the current recorded benchmark execution.



\---


## 🗳️ Wiki-Vote Benchmark

The project was extended with the SNAP Wiki-Vote graph dataset to evaluate
graph traversal performance on a real-world directed network.

### Dataset

The Wiki-Vote dataset contains:

- 7,115 WikiUser nodes
- 103,689 VOTES relationships
- 9 graph-query workloads
- Point lookups
- Indexed lookups
- One-hop traversal
- Two-hop traversal
- Three-hop traversal
- Incoming and outgoing degree counts
- High-degree node traversal
- Global relationship counting

The dataset was loaded independently into both CognoDB Cloud and Neo4j.

### Benchmark Configuration

The final benchmark used:

- 3 warm-up runs per workload
- 30 measured runs per workload
- 9 workloads
- 270 measurements per database
- 100% successful measurements

### Final Results

| Metric | CognoDB | Neo4j |
|---|---:|---:|
| Measurements | 270 | 270 |
| Success rate | 100% | 100% |
| Average latency | 424.429 ms | 180.937 ms |
| P50 latency | 267.629 ms | 177.529 ms |
| P95 latency | 1504.938 ms | 201.874 ms |
| P99 latency | 1573.217 ms | 209.703 ms |
| Maximum latency | 1614.861 ms | 255.048 ms |

Neo4j achieved a 57.37% lower average latency than CognoDB
for the Wiki-Vote benchmark.

At P95, Neo4j achieved an 86.59% lower latency.

The high-degree workload showed the largest workload-level difference:

- CognoDB: 1495.673 ms
- Neo4j: 201.823 ms
- Difference: 86.51%

All nine Wiki-Vote workloads were faster on Neo4j in this test environment.

### Benchmark Output

Wiki-Vote raw measurements are generated locally in:

```text
results/raw/cognodb_wikivote_benchmark.csv
results/raw/neo4j_wikivote_benchmark.csv


### FalkorDB Cross-Database Benchmark

The Wiki-Vote benchmark was extended to include FalkorDB.

FalkorDB was successfully connected, loaded with the Wiki-Vote dataset, benchmarked using the same nine Wiki-Vote workloads, and compared against CognoDB, Neo4j, and Memgraph.

| Database | Measurements | Average Latency (ms) | Median / P50 (ms) | Minimum (ms) | Maximum (ms) | P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| CognoDB | 270 | 424.429 | 267.629 | 257.204 | 1614.861 | 1500.923 |
| Neo4j | 270 | 180.937 | 177.529 | 171.549 | 255.048 | 201.476 |
| Memgraph | 90 | 218.002 | 181.060 | 175.380 | 809.973 | 417.799 |
| FalkorDB | 45 | 36.781 | 35.968 | 32.918 | 44.882 | 43.094 |

FalkorDB recorded the lowest average latency in this benchmark execution at 36.781 ms.

The measurement counts differ between databases because the benchmark runs were executed with different measured-run configurations. Therefore, these results should be interpreted as measurements of the tested executions rather than a perfectly equal-sample statistical comparison.

The generated four-database comparison is saved to:

```text
results/processed/cognodb_vs_neo4j_memgraph_falkordb_wikivote.csv





\## 👨‍💻 Author



\*\*Ravi Raj\*\*



B.E. Computer Science and Business Systems

Chandigarh University



\### Profiles



\- GitHub: `iravi0009`

\- LinkedIn: `raviraj0009`



\---






\## 📜 License



This project is intended for benchmarking, experimentation, research, and educational purposes.



\---

