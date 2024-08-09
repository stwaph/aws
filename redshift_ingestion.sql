COPY myschema.mytable
FROM 's3://my-bucket/data/files/'
IAM_ROLE ‘arn:aws:iam::1234567891011:role/MyRedshiftRole’
FORMAT AS CSV;

CREATE EXTERNAL SCHEMA kafka_schema
FROM KAFKA
BROKER 'broker-1.example.com:9092,broker-2.example.com:9092'
TOPIC 'iot-telemetry-topic'
REGION 'us-east-1'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRoleForMSK';

CREATE MATERIALIZED VIEW iot_telemetry_view
AUTO REFRESH YES
AS SELECT
    kafka_partition,
    kafka_offset,
    kafka_timestamp_type,
    kafka_timestamp,
    CAST(kafka_value AS SUPER) payload
FROM kafka_schema.iot-telemetry-topic;

SELECT
    kafka_timestamp,
    payload:device_id,
    payload:temperature,
    payload:pressure
FROM iot_telemetry_view;

CREATE EXTERNAL SCHEMA postgres_schema
FROM POSTGRES
DATABASE 'mydatabase'
SCHEMA 'public'
URI 'endpoint-for-your-rds-instance.aws-region.rds.amazonaws.com:5432'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRoleForRDS'
SECRET_ARN 'arn:aws:secretsmanager:aws-region:123456789012:secret:my-rds-secret-abc123';


SELECT
    r.order_id,
    r.order_date,
    r.customer_name,
    r.total_amount,
    h.product_name,
    h.category
FROM
    postgres_schema.orders r
    JOIN redshift_schema.product_history h ON r.product_id = h.product_id
WHERE
    r.order_date >= '2024-01-01';


CREATE MATERIALIZED VIEW sales_report AS
SELECT
    r.order_id,
    r.order_date,
    r.customer_name,
    r.total_amount,
    h.product_name,
    h.category,
    h.historical_sales
FROM
    (
        SELECT
            order_id,
            order_date,
            customer_name,
            total_amount,
            product_id
        FROM
            postgres_schema.orders
    ) r
    JOIN redshift_schema.product_history h ON r.product_id = h.product_id;


CREATE MATERIALIZED VIEW orders_summary AS
SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.quantity * oi.price) AS total_revenue,
    MAX(o.order_date) AS latest_order_date
FROM
    aurora_schema.orders o
    JOIN aurora_schema.order_items oi ON o.order_id = oi.order_id
GROUP BY
    o.order_id,
    o.customer_id;


SELECT
	customer_id,
	SUM(total_revenue) AS total_customer_revenue,
	MAX(latest_order_date) AS most_recent_order
FROM
	orders_summary
GROUP BY
	customer_id
ORDER BY
	total_customer_revenue DESC;



