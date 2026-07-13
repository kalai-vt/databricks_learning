# Unity Catalog Quickstart — Short, Simple, Hands-On (~20–25 min)

A trimmed-down version of the full RetailCorp demo (see `../README.md`), for when you only have
20–25 minutes or want the simplest possible path to "aha, I get it." One catalog, one schema, two
tiny tables, one script. Everything is in **`hands_on.sql`** — open it and run each `STEP` block
top-to-bottom as you go through this guide.

## What You Need

- A Databricks workspace with Unity Catalog enabled.
- A running SQL Warehouse or cluster.
- Privilege to create a catalog (or ask an admin to run Step 2 for you).
- `hands_on.sql` open in a SQL editor or notebook, and `cleanup.sql` on hand for the end.

## Step-by-Step

### Step 1 — Confirm Unity Catalog is on (1 min)
Run:
```sql
SELECT CURRENT_METASTORE();
SHOW CATALOGS;
```
**Explain:** "A Metastore is the container that holds everything we're about to build. We don't
create it ourselves — this just proves we're connected to one."

### Step 2 — Create a Catalog (2 min)
```sql
CREATE CATALOG IF NOT EXISTS uc_quickstart;
```
**Explain:** "A Catalog is the top level of `catalog.schema.table`. Think of it as one team's own
database — a clean boundary for a department or project."

### Step 3 — Create a Schema (2 min)
```sql
CREATE SCHEMA IF NOT EXISTS uc_quickstart.retail;
USE CATALOG uc_quickstart;
USE SCHEMA retail;
```
**Explain:** "A Schema is a folder inside the catalog that groups related tables together."

### Step 4 — Create a Managed Table + add data (4 min)
Run the `products` and `orders` table creation + inserts, then:
```sql
SELECT * FROM products;
DESCRIBE TABLE EXTENDED products;
```
**Explain:** "No `LOCATION` was specified, so Unity Catalog picked the storage path and owns the
data — that's a **Managed Table**. Look at `Type = MANAGED` in the output. If you `DROP` this
table, the data is gone too."

### Step 5 — Create a View (3 min)
```sql
CREATE OR REPLACE VIEW order_summary_view AS
SELECT o.order_id, o.customer_name, p.product_name, o.quantity, (o.quantity * p.price) AS total_amount
FROM orders o JOIN products p ON o.product_id = p.product_id;

SELECT * FROM order_summary_view;
```
**Explain:** "A View stores no data of its own — it's a saved query that re-joins `products` and
`orders` live, every time someone queries it."

### Step 6 — Create a Volume (2 min)
```sql
CREATE VOLUME IF NOT EXISTS raw_files;
SHOW VOLUMES IN uc_quickstart.retail;
```
**Explain:** "A Volume is the same governance model, but for raw files instead of tables — CSVs,
images, anything non-tabular. It shows up as a normal filesystem path:
`/Volumes/uc_quickstart/retail/raw_files/`."

### Step 7 — External Table (explain only, 2 min)
Point at the commented example in `hands_on.sql`.
**Explain:** "If I added one clause — `LOCATION 's3://...'` — this becomes an **External Table**.
Same syntax, but now Unity Catalog only manages the metadata; the files stay in that bucket, and
`DROP TABLE` won't delete them. We're skipping running this live because it needs a real cloud
storage path set up by an admin — but the syntax is right there for reference."

### Step 8 — Grant, Revoke, RBAC (5 min — the most important part)
Replace `` `REPLACE_WITH_A_USER_EMAIL` `` with a real second user if you have one, then run:
```sql
GRANT USE CATALOG ON CATALOG uc_quickstart TO `their_email`;
GRANT USE SCHEMA  ON SCHEMA  uc_quickstart.retail TO `their_email`;
GRANT SELECT ON TABLE uc_quickstart.retail.products TO `their_email`;
SHOW GRANTS ON TABLE uc_quickstart.retail.products;
```
**Explain:** "To query a table, a user needs THREE things at once: `USE CATALOG`, `USE SCHEMA`,
and `SELECT` (or `MODIFY` to write). Miss any one and it's Access Denied — that's the whole RBAC
model in one sentence."

If you have a second logged-in user, have them try:
```sql
SELECT * FROM uc_quickstart.retail.products;   -- works
SELECT * FROM uc_quickstart.retail.orders;      -- fails — Access Denied (no grant on orders)
```
Then revoke it back:
```sql
REVOKE SELECT ON TABLE uc_quickstart.retail.products FROM `their_email`;
```

### Step 9 — Lineage (3 min, no SQL needed)
Go to **Catalog Explorer → uc_quickstart → retail → order_summary_view → Lineage tab**.
**Explain:** "Unity Catalog automatically figured out that this view depends on `products` and
`orders` — I never told it that. It tracked it the moment I ran `CREATE VIEW` in Step 5."

### Step 10 — Wrap Up (2 min)
Recap in one breath: *"Catalog → Schema → Table/View/Volume. Managed tables: Unity Catalog owns
the data. External tables: the data stays where it is. Grants: three locks must all be open.
Lineage: automatic, zero config."*

Run `cleanup.sql` when you're fully done (not required immediately — fine to leave it for
follow-up questions first).

## One-Page Cheat Sheet

| Concept | One-liner | Command used |
|---|---|---|
| Metastore | Top-level metadata container, one per region | `SELECT CURRENT_METASTORE();` |
| Catalog | Top of the 3-level name, one per team/dept | `CREATE CATALOG` |
| Schema | Folder inside a catalog | `CREATE SCHEMA` |
| Managed Table | UC owns the data; DROP deletes it | `CREATE TABLE` (no LOCATION) |
| External Table | Data stays in your bucket; DROP keeps it | `CREATE TABLE ... LOCATION '...'` |
| View | Saved query, no data of its own | `CREATE VIEW` |
| Volume | Governed file storage | `CREATE VOLUME` |
| RBAC | 3 locks: catalog + schema + object privilege | `GRANT` / `REVOKE` |
| Lineage | Automatic, zero-config dependency tracking | Catalog Explorer → Lineage tab |

## With Catalog vs Without Unity Catalog — Side by Side

The same 9 concepts, but showing what changes if Unity Catalog **isn't** there (the old,
workspace-scoped Hive Metastore world) versus what you get **with** it. This is the fastest way to
make the "why does this matter?" question click for a beginner.

| Concept | ❌ Without Unity Catalog (Hive Metastore) | ✅ With Unity Catalog | Command (with UC) |
|---|---|---|---|
| **Metastore** | One metastore **per workspace** — Sales, HR, Finance each have their own, invisible to each other | **One** metastore per region, shared by every workspace | `SELECT CURRENT_METASTORE();` |
| **Catalog** | Doesn't exist — no such level at all | Top level of the name; one per team/dept (`retail_sales`, `retail_hr`) | `CREATE CATALOG` |
| **Namespace** | 2-level: `database.table` | 3-level: `catalog.schema.table` — an extra layer to separate departments | `catalog.schema.table` |
| **Schema** | The top level itself (a "database") | A folder **inside** a catalog — one level lower than before | `CREATE SCHEMA` |
| **Managed Table** | Table's storage path is whatever the cluster/admin set up by hand; cleanup is manual | UC auto-picks and owns the storage path; `DROP TABLE` cleanly deletes data too | `CREATE TABLE` (no LOCATION) |
| **External Table** | A `LOCATION` path with no central record of *who* is allowed to read it | Governed by a Storage Credential + External Location; access is GRANT-able like any table | `CREATE TABLE ... LOCATION '...'` |
| **View** | Works, but permission enforcement on it depends on the cluster's ACL config | Saved query, governed identically to a table, everywhere | `CREATE VIEW` |
| **Volume / Files** | Raw files sit in ungoverned DBFS mounts — no GRANT, no audit | Governed, GRANT-able file storage, same rules as tables | `CREATE VOLUME` |
| **RBAC** | Table-level ACLs, enforced only on specifically configured clusters — easy to bypass | 3 locks required everywhere: `USE CATALOG` + `USE SCHEMA` + object privilege | `GRANT` / `REVOKE` |
| **Lineage** | Doesn't exist — you'd trace it by reading code or asking around | Automatic, zero-config, table + column level | Catalog Explorer → Lineage tab |
| **Cross-department query** | Hard/impossible — each workspace's metastore can't see the others | One `SELECT` can join tables across two catalogs in a single statement | `SELECT ... FROM cat_a.s.t1 JOIN cat_b.s.t2` |
| **Auditing "who accessed what"** | Manual, per-cluster logs, easy to miss | Centralized, queryable system table | `SELECT * FROM system.access.audit;` |

**The takeaway to say out loud:** "Unity Catalog doesn't just add a `catalog` word to your table
names — it replaces per-workspace, per-cluster, inconsistently-enforced rules with **one governed
layer** that every workspace, every cluster, and every BI tool obeys the same way."

Want the full enterprise-realistic version with security personas, external storage, and Power BI
lineage? See the main demo one level up: `../README.md`.
