\# CognoDB Cloud Graph Database Benchmark



\## Overview



This project benchmarks query performance of a CognoDB Cloud graph

database using a reproducible synthetic graph dataset and a collection

of representative graph workloads.



The benchmark measures query latency, success rate, returned record

counts, and percentile performance.



\---



\## Database Dataset



The benchmark graph contains:



\- 10,000 Person nodes

\- 1,000 Company nodes

\- 100 Technology nodes



Total nodes:



11,100



Relationships:



\- 10,000 WORKS\_AT

\- 50,000 KNOWS

\- 20,000 USES from Person to Technology

\- 5,000 USES from Company to Technology



Total relationships:



85,000



Total graph elements:



11,100 nodes + 85,000 relationships



\---



\## Dataset Files



The generated dataset contains:



```text

data/generated/

├── persons.csv

├── companies.csv

├── technologies.csv

├── works\_at.csv

├── knows.csv

├── person\_uses.csv

└── company\_uses.csv

