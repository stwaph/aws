from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

# Create a SparkSession
spark = SparkSession.builder \
    .appName("RedshiftSparkJob") \
    .getOrCreate()

# Set Amazon Redshift connection properties
redshift_jdbc_url = "jdbc:redshift://<redshift-endpoint>:<port>/<database>"
redshift_table = "<schema>.<table_name>"
temp_s3_bucket = "s3://<bucket_name>/temp/"
iam_role_arn = "<iam_role_arn>"

# Read data from Amazon S3
s3_data = spark.read.format("parquet") \
    .load("s3://<bucket_name>/player_events/")

# Perform transformations
transformed_data = s3_data.withColumn("transformed_column", lit("transformed_value"))

# Write the transformed data to Amazon Redshift
transformed_data.write \
    .format("io.github.spark_redshift_community.spark.redshift") \
    .option("url", redshift_jdbc_url) \
    .option("dbtable", redshift_table) \
    .option("tempdir", temp_s3_bucket) \
    .option("aws_iam_role", iam_role_arn) \
    .mode("overwrite") \
    .save()


