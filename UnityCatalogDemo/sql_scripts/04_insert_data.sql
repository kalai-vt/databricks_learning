-- =====================================================================
-- 04_insert_data.sql
-- Purpose : INSERT sample data (20 rows each for customers/products/
--           orders/sales, employees; 6 rows for departments)
-- Note    : Mirrors the CSVs in /data. For file-based loading see
--           11_external_table_volume.sql (COPY INTO pattern).
-- =====================================================================

USE CATALOG retail_sales;
USE SCHEMA sales;

INSERT INTO customers VALUES
('C001','Aarav Sharma','aarav.sharma@example.com','Mumbai','Maharashtra',DATE'2022-01-15','Consumer'),
('C002','Priya Nair','priya.nair@example.com','Bengaluru','Karnataka',DATE'2022-02-10','Consumer'),
('C003','Rohan Mehta','rohan.mehta@example.com','Delhi','Delhi',DATE'2022-02-21','Corporate'),
('C004','Sneha Iyer','sneha.iyer@example.com','Chennai','Tamil Nadu',DATE'2022-03-05','Consumer'),
('C005','Karan Malhotra','karan.malhotra@example.com','Pune','Maharashtra',DATE'2022-03-18','Corporate'),
('C006','Ananya Gupta','ananya.gupta@example.com','Hyderabad','Telangana',DATE'2022-04-02','Consumer'),
('C007','Vikram Rao','vikram.rao@example.com','Kolkata','West Bengal',DATE'2022-04-19','Home Office'),
('C008','Ishita Desai','ishita.desai@example.com','Ahmedabad','Gujarat',DATE'2022-05-07','Consumer'),
('C009','Arjun Kapoor','arjun.kapoor@example.com','Jaipur','Rajasthan',DATE'2022-05-25','Corporate'),
('C010','Meera Pillai','meera.pillai@example.com','Kochi','Kerala',DATE'2022-06-11','Consumer'),
('C011','Aditya Verma','aditya.verma@example.com','Lucknow','Uttar Pradesh',DATE'2022-06-30','Home Office'),
('C012','Divya Menon','divya.menon@example.com','Coimbatore','Tamil Nadu',DATE'2022-07-14','Consumer'),
('C013','Siddharth Joshi','siddharth.joshi@example.com','Nagpur','Maharashtra',DATE'2022-08-02','Corporate'),
('C014','Kavya Reddy','kavya.reddy@example.com','Vijayawada','Andhra Pradesh',DATE'2022-08-20','Consumer'),
('C015','Nikhil Bansal','nikhil.bansal@example.com','Chandigarh','Punjab',DATE'2022-09-09','Home Office'),
('C016','Riya Choudhury','riya.choudhury@example.com','Guwahati','Assam',DATE'2022-09-27','Consumer'),
('C017','Manish Agarwal','manish.agarwal@example.com','Indore','Madhya Pradesh',DATE'2022-10-15','Corporate'),
('C018','Pooja Saxena','pooja.saxena@example.com','Bhopal','Madhya Pradesh',DATE'2022-11-03','Consumer'),
('C019','Rahul Bhatt','rahul.bhatt@example.com','Surat','Gujarat',DATE'2022-11-21','Home Office'),
('C020','Neha Kulkarni','neha.kulkarni@example.com','Nashik','Maharashtra',DATE'2022-12-08','Consumer');

INSERT INTO products VALUES
('P001','Wireless Mouse','Electronics','LogiTech Pro',799.00),
('P002','Bluetooth Headphones','Electronics','SoundWave',2499.00),
('P003','Cotton T-Shirt','Apparel','UrbanThreads',599.00),
('P004','Running Shoes','Footwear','SprintFit',3299.00),
('P005','Stainless Steel Bottle','Home & Kitchen','HydroLife',449.00),
('P006','Yoga Mat','Sports & Fitness','FlexiFit',999.00),
('P007','LED Desk Lamp','Home & Kitchen','BrightHome',1299.00),
('P008','Backpack','Accessories','TrailPack',1899.00),
('P009','Smart Watch','Electronics','PulseTech',5999.00),
('P010','Denim Jeans','Apparel','UrbanThreads',1599.00),
('P011','Non-Stick Frying Pan','Home & Kitchen','ChefPro',1199.00),
('P012','Wireless Keyboard','Electronics','LogiTech Pro',1499.00),
('P013','Sports Cap','Accessories','TrailPack',349.00),
('P014','Formal Shirt','Apparel','ClassicWear',1099.00),
('P015','Fitness Tracker Band','Electronics','PulseTech',2999.00),
('P016','Table Lamp','Home & Kitchen','BrightHome',899.00),
('P017','Leather Wallet','Accessories','UrbanThreads',999.00),
('P018','Trekking Shoes','Footwear','SprintFit',3999.00),
('P019','Ceramic Mug Set','Home & Kitchen','HydroLife',599.00),
('P020','Gym Gloves','Sports & Fitness','FlexiFit',499.00);

INSERT INTO orders VALUES
('O1001','C001','P001',DATE'2023-01-05',2,'Delivered'),
('O1002','C002','P003',DATE'2023-01-08',1,'Delivered'),
('O1003','C003','P009',DATE'2023-01-12',1,'Delivered'),
('O1004','C004','P006',DATE'2023-01-15',3,'Delivered'),
('O1005','C005','P012',DATE'2023-01-20',1,'Cancelled'),
('O1006','C006','P002',DATE'2023-01-25',2,'Delivered'),
('O1007','C007','P018',DATE'2023-02-02',1,'Delivered'),
('O1008','C008','P010',DATE'2023-02-06',2,'Delivered'),
('O1009','C009','P007',DATE'2023-02-11',1,'Returned'),
('O1010','C010','P015',DATE'2023-02-14',1,'Delivered'),
('O1011','C011','P004',DATE'2023-02-19',1,'Delivered'),
('O1012','C012','P011',DATE'2023-02-23',1,'Delivered'),
('O1013','C013','P020',DATE'2023-03-01',4,'Delivered'),
('O1014','C014','P005',DATE'2023-03-05',2,'Delivered'),
('O1015','C015','P014',DATE'2023-03-09',1,'Delivered'),
('O1016','C016','P017',DATE'2023-03-14',1,'Delivered'),
('O1017','C017','P008',DATE'2023-03-18',1,'Cancelled'),
('O1018','C018','P019',DATE'2023-03-22',2,'Delivered'),
('O1019','C019','P013',DATE'2023-03-27',3,'Delivered'),
('O1020','C020','P016',DATE'2023-03-30',1,'Delivered');

INSERT INTO sales VALUES
('S2001','O1001',DATE'2023-01-07',1598.00,'West','Online'),
('S2002','O1002',DATE'2023-01-10',599.00,'South','Online'),
('S2003','O1003',DATE'2023-01-14',5999.00,'North','In-Store'),
('S2004','O1004',DATE'2023-01-17',2997.00,'South','Online'),
('S2005','O1005',DATE'2023-01-22',1499.00,'West','Online'),
('S2006','O1006',DATE'2023-01-27',4998.00,'South','In-Store'),
('S2007','O1007',DATE'2023-02-04',3999.00,'East','Online'),
('S2008','O1008',DATE'2023-02-08',3198.00,'West','In-Store'),
('S2009','O1009',DATE'2023-02-13',1299.00,'North','Online'),
('S2010','O1010',DATE'2023-02-16',2999.00,'South','Online'),
('S2011','O1011',DATE'2023-02-21',3299.00,'North','In-Store'),
('S2012','O1012',DATE'2023-02-25',1199.00,'South','Online'),
('S2013','O1013',DATE'2023-03-03',1996.00,'West','Online'),
('S2014','O1014',DATE'2023-03-07',898.00,'South','In-Store'),
('S2015','O1015',DATE'2023-03-11',1099.00,'North','Online'),
('S2016','O1016',DATE'2023-03-16',999.00,'East','Online'),
('S2017','O1017',DATE'2023-03-20',1899.00,'North','In-Store'),
('S2018','O1018',DATE'2023-03-24',1198.00,'North','Online'),
('S2019','O1019',DATE'2023-03-29',1047.00,'West','Online'),
('S2020','O1020',DATE'2023-04-01',899.00,'West','In-Store');

USE CATALOG retail_hr;
USE SCHEMA hr;

INSERT INTO departments VALUES
('D01','Sales','Mumbai','Rajesh Kumar'),
('D02','Human Resources','Bengaluru','Sunita Rao'),
('D03','Finance','Delhi','Anil Kapoor'),
('D04','Marketing','Pune','Deepika Shah'),
('D05','Information Technology','Hyderabad','Vivek Nair'),
('D06','Customer Support','Chennai','Lakshmi Menon');

INSERT INTO employees VALUES
('E101','Rajesh Kumar','D01','Sales Manager',DATE'2018-03-01',1450000,'rajesh.kumar@retailcorp.com'),
('E102','Sunita Rao','D02','HR Manager',DATE'2017-06-15',1350000,'sunita.rao@retailcorp.com'),
('E103','Anil Kapoor','D03','Finance Manager',DATE'2016-11-20',1550000,'anil.kapoor@retailcorp.com'),
('E104','Deepika Shah','D04','Marketing Manager',DATE'2019-01-10',1250000,'deepika.shah@retailcorp.com'),
('E105','Vivek Nair','D05','IT Manager',DATE'2018-07-22',1400000,'vivek.nair@retailcorp.com'),
('E106','Lakshmi Menon','D06','Support Manager',DATE'2019-09-05',1150000,'lakshmi.menon@retailcorp.com'),
('E107','Amit Trivedi','D01','Sales Executive',DATE'2020-02-14',650000,'amit.trivedi@retailcorp.com'),
('E108','Neelam Sharma','D01','Sales Executive',DATE'2020-05-19',620000,'neelam.sharma@retailcorp.com'),
('E109','Rakesh Yadav','D01','Sales Executive',DATE'2021-01-11',600000,'rakesh.yadav@retailcorp.com'),
('E110','Sonal Mishra','D02','HR Executive',DATE'2020-03-25',580000,'sonal.mishra@retailcorp.com'),
('E111','Tarun Chawla','D02','HR Executive',DATE'2021-04-08',560000,'tarun.chawla@retailcorp.com'),
('E112','Kritika Ahuja','D03','Finance Analyst',DATE'2020-06-30',700000,'kritika.ahuja@retailcorp.com'),
('E113','Manoj Pillai','D03','Finance Analyst',DATE'2021-02-17',680000,'manoj.pillai@retailcorp.com'),
('E114','Swati Bhatt','D03','Accountant',DATE'2019-10-12',610000,'swati.bhatt@retailcorp.com'),
('E115','Harish Reddy','D04','Marketing Executive',DATE'2021-05-23',590000,'harish.reddy@retailcorp.com'),
('E116','Payal Jain','D04','Marketing Executive',DATE'2022-01-09',570000,'payal.jain@retailcorp.com'),
('E117','Suresh Iyer','D05','Data Engineer',DATE'2020-08-14',950000,'suresh.iyer@retailcorp.com'),
('E118','Nandini Rao','D05','Data Analyst',DATE'2021-03-02',750000,'nandini.rao@retailcorp.com'),
('E119','Farhan Sheikh','D05','Cloud Engineer',DATE'2022-02-18',980000,'farhan.sheikh@retailcorp.com'),
('E120','Geeta Krishnan','D06','Support Executive',DATE'2021-07-27',520000,'geeta.krishnan@retailcorp.com');

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM retail_sales.sales.customers
UNION ALL SELECT 'products', COUNT(*) FROM retail_sales.sales.products
UNION ALL SELECT 'orders', COUNT(*) FROM retail_sales.sales.orders
UNION ALL SELECT 'sales', COUNT(*) FROM retail_sales.sales.sales
UNION ALL SELECT 'departments', COUNT(*) FROM retail_hr.hr.departments
UNION ALL SELECT 'employees', COUNT(*) FROM retail_hr.hr.employees;
