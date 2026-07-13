# 28 — Cluster Configuration for Unity Catalog (~5 min hands-on)

## The Rule (one sentence)

A cluster can only see Unity Catalog objects if it's created with an **Access Mode** that supports
UC, running **Databricks Runtime 11.3 LTS or higher**. Get this wrong and every UC query fails.

## Access Modes — Compare

| Access Mode | Supports Unity Catalog? | Typical use |
|---|:---:|---|
| **Single User** | ✅ Yes | One person (or a job/service principal) — full language support (SQL, Python, Scala, R) |
| **Shared** | ✅ Yes | Multiple users on one cluster — SQL + Python, with extra process isolation between users |
| **No Isolation Shared** (legacy) | ❌ No | Old-style shared clusters — cannot see Unity Catalog objects at all, only `hive_metastore` |

## Hands-On Steps

1. Left sidebar → **Compute** → **Create Compute**.
2. Under **Access mode**, choose **Single User** (pick your own identity) — the simplest option
   for a personal demo/dev cluster.
3. Under **Databricks Runtime Version**, pick **11.3 LTS** or newer (later is fine — pick the
   current LTS unless a lab specifically needs an older one).
4. Click **Create Compute** and wait for it to start.
5. Attach a notebook to this cluster and run:
   ```sql
   SELECT CURRENT_METASTORE();
   SHOW CATALOGS;
   ```
   You should see your Unity Catalog catalogs. That confirms the cluster is UC-enabled.

## Optional Contrast (if you have an old cluster lying around)

Attach the same notebook to a **No Isolation Shared** cluster (if your workspace still has one)
and re-run `SHOW CATALOGS;` — you'll only see `hive_metastore`-backed objects, or the query will
be blocked entirely, depending on workspace configuration. This is the fastest way to make the
"cluster config matters" point land live.

## Talking Points

- This trips up beginners constantly: "My `CREATE CATALOG` script works for me but fails for my
  teammate" is almost always a cluster access-mode mismatch, not a permissions problem.
- **SQL Warehouses** (Databricks SQL) are UC-enabled by default — this cluster-access-mode concern
  is specific to all-purpose/job clusters, not SQL Warehouses.
- Recommendation for teams: default all new clusters to **Shared** access mode so multiple team
  members can use one cluster while still getting Unity Catalog governance.
