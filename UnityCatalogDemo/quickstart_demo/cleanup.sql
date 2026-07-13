-- Quickstart cleanup — run to reset after the short demo
DROP VIEW IF EXISTS uc_quickstart.retail.order_summary_view;
DROP VOLUME IF EXISTS uc_quickstart.retail.raw_files;
DROP TABLE IF EXISTS uc_quickstart.retail.products;
DROP TABLE IF EXISTS uc_quickstart.retail.orders;
DROP SCHEMA IF EXISTS uc_quickstart.retail CASCADE;
DROP CATALOG IF EXISTS uc_quickstart CASCADE;

SHOW CATALOGS;   -- confirm uc_quickstart is gone
