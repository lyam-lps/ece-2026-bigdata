import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

os.environ["LAB_BUCKET_NAME"] = os.environ["KUBERNETES_NAMESPACE"]
BUCKET = os.environ["LAB_BUCKET_NAME"]
ICEBERG_PACKAGE = "org.apache.iceberg:iceberg-spark-runtime-4.1_2.13:1.11.0"

spark = (
    SparkSession.builder
    .appName("lab-silver-pyspark")
    # 2 cores and 1 GB to stay within the memory limit of the Onyxia service
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    # S3 access, credentials read from the environment
    .config("spark.hadoop.fs.s3a.endpoint", f"https://{os.environ['AWS_S3_ENDPOINT']}")
    .config("spark.hadoop.fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    .config("spark.hadoop.fs.s3a.session.token", os.environ.get("AWS_SESSION_TOKEN", ""))
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    # Iceberg catalog "lab", stored in the bucket
    .config("spark.jars.packages", ICEBERG_PACKAGE)
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.lab", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.lab.type", "hadoop")
    .config("spark.sql.catalog.lab.warehouse", f"s3a://{BUCKET}/warehouse")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# Bronze layer, read directly from S3
users_bronze = spark.read.csv(f"s3a://{BUCKET}/bronze/users.csv", header=True, inferSchema=True, samplingRatio=0.01, multiLine=True)
orders_bronze = spark.read.csv(f"s3a://{BUCKET}/bronze/orders.csv", header=True, inferSchema=True, samplingRatio=0.01, multiLine=True)
print("Session ready, bronze loaded")
