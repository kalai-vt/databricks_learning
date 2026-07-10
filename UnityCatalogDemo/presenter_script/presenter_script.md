# Presenter Script — Unity Catalog Live Demo (45–60 minutes)

**Audience:** Beginners to Databricks, SQL Developers, Data Engineers, BI Developers — no prior
Unity Catalog knowledge.
**Format:** Live Databricks workspace + this repo open side by side (`UnityCatalogDemo/`).
**Before you start:** Have the workspace open with a running SQL Warehouse, `UnityCatalogDemo/`
cloned or imported as notebooks, and `diagrams/architecture_diagrams.md` open in a second tab for
quick reference.

Speaker notes are written as **"SAY:"** (read roughly as-is) and **"DO:"** (actions to take on
screen). Timings are cumulative guidance, not a stopwatch — adjust pacing to the room.

---

## 0:00 – 0:03 — Welcome & Agenda

**SAY:**
"Hi everyone, thanks for joining. Over the next 45 to 60 minutes we're going to learn Unity
Catalog — Databricks' governance layer for data — hands-on. I'm not going to just talk at slides;
we're going to build a real, small governance setup for a fictional retail company, live, in
front of you.

By the end you'll be able to answer: what is Unity Catalog, why it exists, how it's different from
the old Hive Metastore, and how to create catalogs, schemas, tables, views, permissions, and see
lineage — all with your own hands if you follow along.

Our scenario: RetailCorp, a retail company with three departments — Sales, HR, and Finance. Each
department is going to get its own catalog, its own data, and its own access rules. Let's go."

**DO:** Show `docs/02_business_scenario.md` for 10 seconds — just the entity diagram.

---

## 0:03 – 0:10 — Why Unity Catalog Exists (concept only, no notebook yet)

**SAY:**
"Before we touch any SQL, quick context — why does this even exist? Databricks used to rely on
something called the Hive Metastore. Each workspace had its own, completely separate metastore."

**DO:** Open `diagrams/architecture_diagrams.md`, show Diagram 1 (Legacy Hive Metastore).

**SAY:**
"Notice each workspace is its own island. If Sales, HR, and Finance each had their own workspace,
there was no shared place to say 'here's who can see what across the whole company.' Permissions
were enforced per-cluster and were honestly easy to bypass. There was no lineage — no way to
answer 'where did this number come from?' And raw files sitting in cloud storage were basically
ungoverned.

Unity Catalog fixes all of that with one governance layer shared across every workspace."

**DO:** Show Diagram 2 (Unity Catalog).

**SAY:**
"Same three departments, same three workspaces — but now there's one Metastore underneath all of
them. Grants, lineage, and audit logs are defined once and enforced everywhere. That's the whole
pitch. Let's look at exactly how it's structured."

**Transition:** "Let's zoom into the architecture for thirty seconds, then we start building."

---

## 0:10 – 0:14 — Architecture & Components

**DO:** Show Diagram 3 (Object Hierarchy) from `diagrams/architecture_diagrams.md`.

**SAY:**
"Everything in Unity Catalog follows this hierarchy: Metastore at the top — one per cloud region.
Underneath it, Catalogs. Underneath each catalog, Schemas — think of a schema as a folder.
Underneath each schema: Tables, Views, and Volumes.

This gives us a three-level name for anything: catalog dot schema dot table. Compare that to the
old world, which only had database dot table — two levels. That third level, the catalog, is what
lets us cleanly give Sales, HR, and Finance their own space."

**Transition:** "Enough theory — let's open a real notebook and create our first objects."

---

## 0:14 – 0:17 — Notebook 1: The Metastore

**DO:** Open `notebooks/01_Create_Metastore/01_Create_Metastore.sql`. Run `SELECT CURRENT_METASTORE();`

**SAY:**
"First thing to know: you don't create a Metastore with SQL. It's created once, by an admin, in
the Account Console — because it sits above all our workspaces. What we *can* do from SQL is
verify we're connected to one."

**DO:** Run the cell. Point at the returned ID.

**SAY:**
"That confirms Unity Catalog is active for this workspace. Now let's run `SHOW CATALOGS` to see
what's already here before we add our own."

**DO:** Run `SHOW CATALOGS;`

**SAY:**
"You'll always see `main`, `system`, and `samples` out of the box. And — this one's important —
`hive_metastore`. That's the legacy metastore we just talked about, still visible so you can
migrate off it gradually. It's literally sitting right next to Unity Catalog as a read-only
catalog."

**Transition:** "Now let's create our own catalogs — one per department."

---

## 0:17 – 0:21 — Notebook 2: Creating Catalogs

**DO:** Open `notebooks/02_Create_Catalogs/02_Create_Catalogs.sql`. Run the three `CREATE CATALOG` statements.

**SAY:**
"Three departments, three catalogs: `retail_sales`, `retail_hr`, `retail_finance`. Notice the
syntax — it's just standard SQL, `CREATE CATALOG IF NOT EXISTS`, with a comment for
documentation. No cloud storage path needed; Unity Catalog handles that for us automatically."

**DO:** Run `SHOW CATALOGS;` again, then `DESCRIBE CATALOG EXTENDED retail_sales;`

**SAY:**
"See the `Storage Root` it picked automatically? That's a managed location under our Metastore's
storage — we didn't configure any bucket paths ourselves. This is the 'Managed' pattern, and
we'll come back to it."

**Transition:** "Catalogs are the top level. Next, schemas — the folders inside each catalog."

---

## 0:21 – 0:24 — Notebook 3: Creating Schemas

**DO:** Open `notebooks/03_Create_Schemas/03_Create_Schemas.sql`. Run the three `CREATE SCHEMA` statements, then `USE CATALOG` / `USE SCHEMA`.

**SAY:**
"One schema per catalog to keep this simple: `sales` inside `retail_sales`, `hr` inside
`retail_hr`, `finance` inside `retail_finance`. Now watch — I'll set my session context with `USE
CATALOG` and `USE SCHEMA`, exactly like `USE DATABASE` in a normal SQL engine, just with one extra
level."

**DO:** Run `SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();`

**Transition:** "Context is set. Let's create actual tables and load some data."

---

## 0:24 – 0:30 — Notebook 4 & 5: Managed Tables + Loading Data

**DO:** Open `notebooks/04_Create_Tables/04_Create_Managed_Tables.sql`. Run the `customers` table creation.

**SAY:**
"Here's our first table — `customers`. Notice: no `LOCATION` clause anywhere. That single fact
makes this a **Managed Table** — Unity Catalog owns both the metadata *and* the data files. If I
drop this table later, the data is gone too. That's the tradeoff for the convenience of not having
to manage storage paths ourselves."

**DO:** Run the remaining `CREATE TABLE` statements for `products`, `orders`, `sales`, then switch catalog and create `departments`/`employees`.

**SAY:**
"Same pattern for products, orders, and our sales fact table — plus, over in the HR catalog,
departments and employees. Notice I added a comment on the `salary` column flagging it as
sensitive — we'll enforce that with permissions shortly."

**DO:** Open `notebooks/05_Load_Data/05_Insert_Data.sql`, run the inserts (or run only 2-3 for time and mention the rest are identical pattern).

**SAY:**
"I'm loading twenty sample rows into each table with plain `INSERT` statements — fine for a demo.
In production you'd use `COPY INTO` from a Volume, which we'll see in a few minutes."

**DO:** Run the row-count verification query.

**Transition:** "Data's in. Now let's build a view — this becomes really important later when we
talk about lineage."

---

## 0:30 – 0:34 — Notebook 6: Creating Views

**DO:** Open `notebooks/06_Create_Views/06_Create_Views.sql`. Run `CREATE OR REPLACE VIEW sales_summary_view`.

**SAY:**
"This view joins customers, products, orders, and sales into one clean, denormalized row per
order — exactly what a BI tool wants to consume. Remember: a view stores no data of its own, it's
just a saved query re-run every time."

**DO:** Run `SELECT * FROM sales_summary_view LIMIT 10;`

**SAY:**
"Now the HR equivalent — but watch what I do differently here."

**DO:** Run the `employee_department_view` creation, pointing at the SELECT list.

**SAY:**
"I deliberately left out `salary` and `email` from this view. Anyone with access to this view
*cannot* see compensation data, even if they never touch the underlying `employees` table
directly. That's a simple, powerful governance pattern — filtering by omission."

**Transition:** "Speaking of who can see what — let's talk security. This is the heart of Unity
Catalog."

---

## 0:34 – 0:44 — Security Demo: RBAC, Grant, Revoke, Access Denied

**DO:** Open `security_demo/02_grant_matrix.md` and show the table briefly.

**SAY:**
"We have four personas: an Admin with full access everywhere, a Sales user, an HR user, and a
Finance user who needs a little bit of both worlds. Let's grant their access."

**DO:** Open `notebooks/07_Grant_Permissions/07_Grant_Permissions.sql`. Run the Sales grants section.

**SAY:**
"Look closely at this pattern — it's the single most important thing to remember about Unity
Catalog permissions. To query a table, a user needs THREE things at once: `USE CATALOG` on the
catalog, `USE SCHEMA` on the schema, and `SELECT` — or `MODIFY` for write access — on the actual
table. Miss any one of those three, and you get Access Denied, even if the other two are granted.
It's a layered lock, not a single switch."

**DO:** Run the HR grants (`ALL PRIVILEGES ON SCHEMA`) and Finance grants (narrow `SELECT` on the view only).

**SAY:**
"For Finance, notice I did NOT grant access to the raw `orders` or `sales` tables — only to the
summary view. That's least privilege in action: give exactly the access needed, nothing more."

**DO:** Open `security_demo/03_access_denied_demo.sql`. If you have a second logged-in session/browser profile as `sales_user`, switch to it live. Otherwise, narrate the expected errors.

**SAY:**
"Now let's prove it. As the Sales user, I can query customers just fine..."

**DO:** Run `SELECT * FROM retail_sales.sales.customers LIMIT 5;` as sales_user — succeeds.

**SAY:**
"...but if I try to touch HR data..."

**DO:** Run `SELECT * FROM retail_hr.hr.employees LIMIT 5;` as sales_user.

**SAY:**
"Access Denied — 'User does not have USE CATALOG on Catalog retail_hr.' That's the exact error
you'll see in real life. This is enforced identically whether you're in a notebook, the SQL
editor, or Power BI connected over ODBC — one governance layer, zero exceptions."

**DO:** Open `notebooks/08_Revoke_Permissions/08_Revoke_Permissions.sql`. Run the `REVOKE USE CATALOG` example.

**SAY:**
"Revoking works the same way, just flipped. If I revoke `USE CATALOG` from Finance on their own
catalog, every query they run against it fails immediately — even though their table-level grants
technically still exist underneath. Revoking the parent lock is the fastest way to fully cut off
access."

**Transition:** "Now let's look at a different kind of table — one where the data lives outside
Unity Catalog's own storage."

---

## 0:44 – 0:49 — Notebook 9 & 10: External Tables and Volumes

**DO:** Open `notebooks/09_External_Table/09_Create_External_Table.sql`. Show the diagram in the notebook (Storage Credential → External Location → External Table).

**SAY:**
"Sometimes data has to stay exactly where it is — say, Finance's ledger extract is written by an
upstream SAP job straight into a specific S3 bucket, and other tools depend on it staying there.
For that we use an External Table. Three pieces work together: a Storage Credential — basically a
cloud IAM role Unity Catalog is allowed to use — an External Location, which is a governed path
using that credential — and finally the External Table itself, which just points at a location
inside that path."

**DO:** Run the `CREATE TABLE finance_ledger ... LOCATION 's3://...'` statement. Run `DESCRIBE TABLE EXTENDED` and point at `Type = EXTERNAL`.

**SAY:**
"Compare that to `customers` earlier, which said `Type = MANAGED`. Same `CREATE TABLE` syntax,
one clause — `LOCATION` — is the entire difference. And critically: if I drop this external
table, only the metadata goes away. The files in S3 are untouched. Drop a Managed Table, though,
and the data is gone for good."

**DO:** Open `notebooks/10_Volumes/10_Create_Volume.sql`. Run `CREATE VOLUME raw_files`.

**SAY:**
"One more object type: Volumes. These govern access to files that AREN'T structured tables — raw
CSVs waiting to be loaded, images, model files. Before Volumes, this kind of data sat in ungoverned
DBFS mounts, completely outside Unity Catalog's permission model. Now it's a first-class,
GRANT-able object right next to our tables."

**Transition:** "Let's run a few real queries against everything we've built, including one that
spans two catalogs."

---

## 0:49 – 0:53 — Notebook 11: Query Examples

**DO:** Open `notebooks/11_Query_Data/11_Query_Examples.sql`. Run the revenue-by-category query and the cross-catalog join.

**SAY:**
"This query joins `retail_sales` and `retail_hr` — two completely different catalogs — in a
single statement. That's trivial now, because both live under the same Metastore. Under the old
Hive Metastore model, this kind of cross-workspace join often wasn't even possible."

**Transition:** "Last big concept — let's see how Unity Catalog tracks where all this data came
from, automatically."

---

## 0:53 – 0:58 — Notebook 12: Lineage Demo

**DO:** Open `notebooks/12_Lineage_Demo/12_Lineage_Demo.sql`. Switch to the Databricks UI, navigate to Catalog Explorer → `retail_sales` → `sales` → `sales_summary_view` → **Lineage** tab.

**SAY:**
"Remember that view we built — `sales_summary_view`? It was built by joining four tables:
customers, orders, products, and sales. Watch what happens when I open its Lineage tab in Catalog
Explorer."

**DO:** Show the lineage graph live — upstream tables feeding the view.

**SAY:**
"Unity Catalog figured this out completely automatically. I never told it 'this view depends on
these four tables' — it parsed the query the moment I ran `CREATE VIEW` and recorded it. If I flip
to the Columns tab, it even tracks lineage at the column level — this `amount` column traces
directly back to the `sales` table's `amount` column.

Now imagine we connect Power BI to this view and build a dashboard the CFO checks every Monday.
The very first time Power BI queries this view, it shows up right here as a downstream node too —
automatically. So six months from now, if someone asks 'where does this number in the CFO's
dashboard come from,' the answer isn't tribal knowledge — it's this graph."

**DO:** (Optional, if time and a system schema is enabled) Run the `system.access.table_lineage` query.

**Transition:** "That's the full picture. Let's wrap up."

---

## 0:58 – 1:00 — Recap & Cleanup Note

**SAY:**
"Let's recap what we just built and why it matters. We created three catalogs mapping to three
real departments. We created schemas, managed tables, and views. We enforced access with GRANT and
REVOKE, and proved it live with Access Denied errors. We registered an External Table for data
that has to stay put, and a Volume for governed file storage. And we saw lineage tracked
completely automatically from raw tables all the way to a view.

Everything you saw today — every SQL statement — is in the `UnityCatalogDemo` repo, organized
notebook by notebook, plus a cleanup script if you want to tear this down and re-run it yourself.

That's Unity Catalog: one governance layer, one namespace, one set of rules, enforced everywhere.
Questions?"

**DO:** Open `interview_questions/interview_questions.md` if there's time for a rapid-fire Q&A
round, or leave it as a takeaway resource. Mention `notebooks/13_Cleanup/13_Cleanup.sql` exists
for anyone re-running the demo in their own workspace, but skip running it live to preserve the
environment for follow-up questions.

---

## Timing Cheat Sheet (compress to 45 min if needed)

| Block | Full (60 min) | Compressed (45 min) |
|---|---|---|
| Welcome + Why UC | 10 min | 6 min |
| Architecture | 4 min | 2 min |
| Metastore/Catalog/Schema (NB 1-3) | 10 min | 7 min |
| Tables/Data/Views (NB 4-6) | 10 min | 8 min |
| Security demo (NB 7-8) | 10 min | 10 min *(don't cut — most requested topic)* |
| External Table/Volume (NB 9-10) | 5 min | 4 min |
| Query examples (NB 11) | 4 min | 2 min |
| Lineage (NB 12) | 5 min | 4 min |
| Recap/Q&A | 2 min | 2 min |

If you must cut something, cut the compressed architecture walkthrough (point at the diagram
instead of narrating every layer) — never cut the security/access-denied demo, it's consistently
the highest-impact moment for this audience.
