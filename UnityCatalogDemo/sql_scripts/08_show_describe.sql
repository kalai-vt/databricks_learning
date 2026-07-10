-- =====================================================================
-- 08_show_describe.sql
-- Purpose : SHOW / DESCRIBE reference commands used throughout the demo
-- =====================================================================

-- SHOW ---------------------------------------------------------------
SHOW CATALOGS;
SHOW SCHEMAS IN retail_sales;
SHOW TABLES IN retail_sales.sales;
SHOW VIEWS IN retail_sales.sales;
SHOW VOLUMES IN retail_sales.sales;
SHOW COLUMNS IN retail_sales.sales.orders;
SHOW CREATE TABLE retail_sales.sales.orders;
SHOW GRANTS ON CATALOG retail_sales;
SHOW GRANTS ON TABLE retail_sales.sales.orders;
SHOW EXTERNAL LOCATIONS;
SHOW STORAGE CREDENTIALS;

-- DESCRIBE -------------------------------------------------------------
DESCRIBE CATALOG EXTENDED retail_sales;
DESCRIBE SCHEMA EXTENDED retail_sales.sales;
DESCRIBE TABLE retail_sales.sales.orders;
DESCRIBE TABLE EXTENDED retail_sales.sales.orders;
DESCRIBE VOLUME retail_sales.sales.raw_files;
DESCRIBE HISTORY retail_sales.sales.customers;   -- Delta table version history

-- information_schema equivalents --------------------------------------
SELECT * FROM retail_sales.information_schema.tables;
SELECT * FROM retail_sales.information_schema.columns WHERE table_name = 'orders';
SELECT * FROM retail_sales.information_schema.table_privileges;
