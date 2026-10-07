CREATE DATABASE customer_retention;
USE customer_retention;

CREATE TABLE customers(
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen TINYINT,
    partner TINYINT,
    dependents TINYINT
);

CREATE TABLE contracts(
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20),
    contract_type VARCHAR(30),

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)
);

CREATE TABLE services(

    service_id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id VARCHAR(20),

    phone_service VARCHAR(10),

    multiple_lines VARCHAR(30),

    internet_service VARCHAR(30),

    online_security VARCHAR(30),

    online_backup VARCHAR(30),

    device_protection VARCHAR(30),

    tech_support VARCHAR(30),

    streaming_tv VARCHAR(30),

    streaming_movies VARCHAR(30),

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)

);

CREATE TABLE billing(

    billing_id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id VARCHAR(20),

    tenure INT,

    paperless_billing VARCHAR(10),

    payment_method VARCHAR(50),

    monthly_charges DECIMAL(10,2),

    total_charges DECIMAL(10,2),

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)

);

CREATE TABLE customer_status(

    status_id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id VARCHAR(20),

    churn TINYINT,

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)

);

CREATE TABLE stg_customer_raw (

customerID VARCHAR(20),

gender VARCHAR(10),

SeniorCitizen INT,

Partner VARCHAR(5),

Dependents VARCHAR(5),

tenure INT,

PhoneService VARCHAR(5),

MultipleLines VARCHAR(30),

InternetService VARCHAR(30),

OnlineSecurity VARCHAR(30),

OnlineBackup VARCHAR(30),

DeviceProtection VARCHAR(30),

TechSupport VARCHAR(30),

StreamingTV VARCHAR(30),

StreamingMovies VARCHAR(30),

Contract VARCHAR(30),

PaperlessBilling VARCHAR(5),

PaymentMethod VARCHAR(50),

MonthlyCharges DECIMAL(10,2),

TotalCharges VARCHAR(20),

Churn VARCHAR(5)

);

SELECT COUNT(*) FROM stg_customer_raw;

SELECT
COUNT(*) AS total_rows,
COUNT(DISTINCT customerID) AS unique_customers
FROM stg_customer_raw;

SELECT customerID, TotalCharges
FROM stg_customer_raw
WHERE TRIM(TotalCharges) = ''
LIMIT 10;

CREATE TABLE ingestion_log (

id INT AUTO_INCREMENT PRIMARY KEY,

filename VARCHAR(100),

row_count INT,

load_time DATETIME,

status VARCHAR(20)

);

INSERT INTO ingestion_log
(filename, row_count, load_time, status)

VALUES
('customer_churn.csv',7043,NOW(),'SUCCESS');

SELECT * FROM ingestion_log;

INSERT INTO customers
(
customer_id,
gender,
senior_citizen,
partner,
dependents
)

SELECT

customerID,

gender,

SeniorCitizen,

CASE
WHEN Partner='Yes' THEN 1
ELSE 0
END,

CASE
WHEN Dependents='Yes' THEN 1
ELSE 0
END

FROM stg_customer_raw;

SELECT COUNT(*) FROM customers;

INSERT INTO contracts
(
customer_id,
contract_type
)

SELECT

customerID,
Contract

FROM stg_customer_raw;

SELECT COUNT(*) FROM contracts;

INSERT INTO services
(
customer_id,
phone_service,
multiple_lines,
internet_service,
online_security,
online_backup,
device_protection,
tech_support,
streaming_tv,
streaming_movies
)

SELECT

customerID,

PhoneService,

MultipleLines,

InternetService,

OnlineSecurity,

OnlineBackup,

DeviceProtection,

TechSupport,

StreamingTV,

StreamingMovies

FROM stg_customer_raw;

SELECT COUNT(*) FROM services;

INSERT INTO billing
(
customer_id,
tenure,
paperless_billing,
payment_method,
monthly_charges,
total_charges
)

SELECT

customerID,

tenure,

PaperlessBilling,

PaymentMethod,

MonthlyCharges,

CAST(
NULLIF(TRIM(TotalCharges),'')
AS DECIMAL(10,2))

FROM stg_customer_raw;

SELECT COUNT(*) FROM billing;

INSERT INTO customer_status
(
customer_id,
churn
)

SELECT

customerID,

CASE
WHEN Churn='Yes' THEN 1
ELSE 0
END

FROM stg_customer_raw;

SELECT COUNT(*) FROM customer_status;

SELECT
(SELECT COUNT(*) FROM customers) customers,

(SELECT COUNT(*) FROM contracts) contracts,

(SELECT COUNT(*) FROM services) services,

(SELECT COUNT(*) FROM billing) billing,

(SELECT COUNT(*) FROM customer_status) status_table;

SELECT

c.customer_id,

c.gender,

ct.contract_type,

b.monthly_charges,

cs.churn

FROM customers c

JOIN contracts ct
ON c.customer_id = ct.customer_id

JOIN billing b
ON c.customer_id = b.customer_id

JOIN customer_status cs
ON c.customer_id = cs.customer_id

LIMIT 10;

SELECT COUNT(*) AS total_customers
FROM customers;

SELECT COUNT(*) AS churned_customers
FROM customer_status
WHERE churn = 1;

SELECT COUNT(*) AS active_customers
FROM customer_status
WHERE churn = 0;

SELECT
    ROUND(
        SUM(churn) * 100.0 / COUNT(*),
        2
    ) AS churn_rate
FROM customer_status;

SELECT
    c.customer_id,
    c.gender,
    ct.contract_type,
    b.monthly_charges,
    b.total_charges,
    b.payment_method,
    s.internet_service,
    cs.churn
FROM customers c
JOIN contracts ct
    ON c.customer_id = ct.customer_id
JOIN billing b
    ON c.customer_id = b.customer_id
JOIN services s
    ON c.customer_id = s.customer_id
JOIN customer_status cs
    ON c.customer_id = cs.customer_id
LIMIT 10;

CREATE OR REPLACE VIEW v_high_risk_customers AS
SELECT
    c.customer_id,
    c.gender,
    ct.contract_type,
    b.monthly_charges,
    s.internet_service,
    cs.churn
FROM customers c
JOIN contracts ct
    ON c.customer_id = ct.customer_id
JOIN billing b
    ON c.customer_id = b.customer_id
JOIN services s
    ON c.customer_id = s.customer_id
JOIN customer_status cs
    ON c.customer_id = cs.customer_id
WHERE
    ct.contract_type = 'Month-to-month'
    AND b.monthly_charges > 70
    AND s.internet_service <> 'No'
    AND cs.churn = 1;

SELECT *
FROM v_high_risk_customers
LIMIT 10;

SHOW FULL TABLES
WHERE Table_type = 'VIEW';

DESCRIBE customer_status;

SHOW CREATE VIEW v_high_risk_customers;

ALTER TABLE ingestion_log
ADD COLUMN reason VARCHAR(500);

DESCRIBE ingestion_log;

ALTER TABLE ingestion_log
CHANGE COLUMN load_time loaded_at DATETIME;

DESCRIBE customers;
DESCRIBE contracts;
DESCRIBE billing;
DESCRIBE customer_status;

CREATE TABLE pipeline_run_log (
    run_id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255),
    rows_inserted INT,
    rows_updated INT,
    rows_unchanged INT,
    run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE pipeline_run_log;

SELECT *
FROM customers
WHERE customer_id = '7590-VHVEG';

SELECT *
FROM billing
WHERE customer_id = '7590-VHVEG';

SELECT
    COUNT(*) AS total_rows,
    SUM(gender IS NULL) AS null_gender,
    SUM(senior_citizen IS NULL) AS null_senior,
    SUM(partner IS NULL) AS null_partner,
    SUM(dependents IS NULL) AS null_dependents
FROM customers;

SELECT
    senior_citizen,
    partner,
    dependents,
    COUNT(*) AS count
FROM customers
GROUP BY senior_citizen, partner, dependents
ORDER BY count DESC;

SET SQL_SAFE_UPDATES = 0;
DELETE b1
FROM billing b1
JOIN billing b2
  ON b1.customer_id = b2.customer_id
 AND b1.billing_id > b2.billing_id
WHERE b1.billing_id IS NOT NULL;
 
SELECT COUNT(*) AS total_billing
FROM billing;

SELECT COUNT(DISTINCT customer_id) AS distinct_customers
FROM billing;

SHOW INDEX FROM billing;

ALTER TABLE billing
ADD UNIQUE KEY uq_billing_customer_id (customer_id);

SHOW INDEX FROM billing;
 