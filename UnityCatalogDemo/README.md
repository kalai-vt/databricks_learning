# Unity Catalog Demo — RetailCorp

A complete, hands-on Databricks Unity Catalog demo project built for a **45–60 minute technical
learning session**. Audience: beginners to Databricks, SQL Developers, Data Engineers, and BI
Developers — no prior Unity Catalog knowledge assumed.

Business scenario: **RetailCorp**, a retail company with three departments — **Sales**, **HR**,
and **Finance** — each with its own catalog, schema, data, and access rules. See
`docs/02_business_scenario.md` for the full story.

## In a Hurry? Short Version First

Only have 20–25 minutes, or want the simplest possible walkthrough? Start with
[`quickstart_demo/README.md`](./quickstart_demo/README.md) — one catalog, one schema, two tiny
tables, a single `hands_on.sql` script covering every core concept with minimal setup. Come back
here for the full 45–60 minute enterprise-realistic version.

## New to the Platform Setup Side? Start Even Earlier

If your course/session covers **Metastore creation, cluster access modes, and cloud storage
credentials** first (the admin/platform setup side, before any catalog exists), start with
[`platform_setup_demo/README.md`](./platform_setup_demo/README.md) — a ~30 min companion demo
covering: Intro to Unity Catalog, the UC vs Hive Metastore object model, creating a Metastore,
UC-compatible cluster configuration, and configuring Storage Credentials / External Locations for
cloud storage access.

## Quick Start (Full Version)

1. **Read first:** `docs/01_concepts_overview.md` for all 21 concepts,
   `docs/03_dbfs_vs_hive_metastore_vs_unity_catalog.md` for the DBFS vs Hive Metastore vs Unity
   Catalog distinction (a common early point of confusion), and `diagrams/architecture_diagrams.md`
   for the ASCII architecture pictures.
2. **Run the demo:** import `notebooks/01..13` into a Databricks workspace in order (they are
   plain-text `.sql` files in Databricks' notebook-source format — File → Import → File in the
   Databricks UI, or use the Databricks CLI/Repos). Each notebook contains explanation, runnable
   SQL, and expected output.
3. **Or run pure SQL:** everything also exists as standalone scripts in `sql_scripts/`, numbered
   in the same order, with no markdown — copy-paste into a SQL editor / DBSQL warehouse.
4. **Presenting?** Follow `presenter_script/presenter_script.md` — it has exact talking points,
   transitions, and a timing cheat sheet for compressing to 45 minutes.
5. **Teaching security?** `security_demo/` has the full grant matrix and a scripted
   Access-Denied walkthrough across four personas.
6. **Wrapping up?** `notebooks/13_Cleanup` / `sql_scripts/12_cleanup.sql` tears everything down.

## Folder Structure

```
UnityCatalogDemo/
├── README.md                      This file
├── data/                          6 sample CSVs (~20 rows each)
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── sales.csv
│   ├── employees.csv
│   └── departments.csv
├── quickstart_demo/                Short (~20-25 min) simplified hands-on version
│   ├── README.md
│   ├── hands_on.sql
│   └── cleanup.sql
├── notebooks/                     13 Databricks SQL notebooks (import into a workspace)
│   ├── 01_Create_Metastore/
│   ├── 02_Create_Catalogs/
│   ├── 03_Create_Schemas/
│   ├── 04_Create_Tables/
│   ├── 05_Load_Data/
│   ├── 06_Create_Views/
│   ├── 07_Grant_Permissions/
│   ├── 08_Revoke_Permissions/
│   ├── 09_External_Table/
│   ├── 10_Volumes/
│   ├── 11_Query_Data/
│   ├── 12_Lineage_Demo/
│   └── 13_Cleanup/
├── sql_scripts/                   Same DDL/DML as pure, copy-pasteable .sql files
│   ├── 01_create_catalog.sql ... 12_cleanup.sql
├── security_demo/                 RBAC deep dive: users, grant matrix, access-denied demo
│   ├── 01_setup_users_groups.sql
│   ├── 02_grant_matrix.md
│   └── 03_access_denied_demo.sql
├── lineage_demo/                  customers/orders -> view -> Power BI walkthrough
│   └── lineage_walkthrough.md
├── diagrams/                      ASCII architecture diagrams
│   └── architecture_diagrams.md
├── interview_questions/           Q&A per concept section
│   └── interview_questions.md
├── presenter_script/               Word-for-word presenter script with timings
│   └── presenter_script.md
├── slides/                        PowerPoint deck + its markdown source
│   ├── slide_content.md
│   ├── build_pptx.py
│   └── UnityCatalog_Demo_Slides.pptx
└── docs/                          Concept reference + business scenario
    ├── 01_concepts_overview.md
    ├── 02_business_scenario.md
    └── 03_dbfs_vs_hive_metastore_vs_unity_catalog.md
```

## What This Demo Covers

**Concepts:** What is Unity Catalog · Why it was introduced · Problems with legacy Hive Metastore
· Hive Metastore vs Unity Catalog · Architecture · Components · Metastore · Catalog · Schema ·
Tables · Views · Volumes · External Locations · Storage Credentials · Managed Tables · External
Tables · Data Governance · RBAC · Data Lineage · Sharing Data (Delta Sharing) · Catalog Explorer.

**Hands-on build:** 3 catalogs (`retail_sales`, `retail_hr`, `retail_finance`), 3 schemas, 6
managed tables, 1 external table, 2 views, 1 volume, a full RBAC grant/revoke matrix across 4
personas with a live Access-Denied demonstration, and an automatic table + column lineage chain
ending at a Power BI dashboard.

## Data Model

```
retail_sales.sales:   customers, products, orders, sales (fact), sales_summary_view, raw_files (volume)
retail_hr.hr:          departments, employees, employee_department_view
retail_finance.finance: finance_ledger (external table)
```

## Requirements

- A Databricks workspace with Unity Catalog enabled (any current Databricks Runtime — this demo
  uses standard SQL, `CREATE CATALOG`/`CREATE VOLUME`/`GRANT` syntax available on all supported
  runtimes) and a running SQL Warehouse or cluster.
- Privileges to create catalogs (or an admin who pre-creates them from `sql_scripts/01_create_catalog.sql`).
- For the security demo: 3-4 additional workspace users/groups (see `security_demo/01_setup_users_groups.sql`).
- To regenerate the slide deck: `pip install python-pptx && python3 slides/build_pptx.py`.

## Regenerating Sample Data

The CSVs in `data/` are the source of truth for every `INSERT` statement in `notebooks/05` and
`sql_scripts/04`. If you change the CSVs, update those two files to match (kept as literal
`INSERT ... VALUES` for a friction-free live demo — no cluster/DBFS upload required to get started).
