# 29 — Configure Access to Cloud Storage: Lecture / Concepts (~4 min)

## The Two Objects, and Why They're Separate

```
   Cloud IAM Role                Named, Governed Path
  (identity only)                (path + which identity to use)

  Storage Credential   ────uses────▶   External Location   ────used by────▶  External Table
  "unity-catalog-role"                 "s3://bucket/prefix/"                 or External Volume
```

| Object | Answers | Created by |
|---|---|---|
| **Storage Credential** | "*Which* cloud identity is Unity Catalog allowed to assume?" | Admin (needs cloud IAM trust) |
| **External Location** | "*Which path*, using *which* credential, is governed for use?" | Admin (or delegated privilege) |

- A single Storage Credential can back **multiple** External Locations (e.g. one IAM role trusted
  for several buckets/prefixes).
- Once an External Location exists, a regular user with the right grant (`CREATE EXTERNAL TABLE`,
  `READ FILES`, `WRITE FILES` on that location) can create External Tables/Volumes inside it —
  they never touch the underlying cloud credential directly.
- This same mechanism is what backed the Metastore's **own root storage** in the "Create
  Metastore" step — a Storage Credential + path, just wired up automatically by the setup wizard.

## Why It's a Separate, Admin-Gated Step

Storage Credentials are the **only** place in Unity Catalog that directly touches real cloud IAM
trust. Everything else (catalogs, schemas, grants) is pure Unity Catalog metadata with no direct
cloud access implications — which is why `CREATE STORAGE CREDENTIAL` and `CREATE EXTERNAL
LOCATION` are high-trust, typically admin-only privileges, while `CREATE CATALOG` can safely be
delegated to more people.

## What We'll Build Next (Demo, topic 30)

1. An IAM role in AWS trusted by Databricks, scoped to one S3 bucket.
2. A **Storage Credential** in Unity Catalog wrapping that role.
3. An **External Location** pointing at `s3://retailcorp-external-data/` using that credential.
4. One External Table created inside it, to prove read/write actually works end to end.
