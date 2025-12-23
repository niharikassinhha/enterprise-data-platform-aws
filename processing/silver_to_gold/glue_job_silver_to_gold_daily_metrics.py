from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    sum as _sum,
    round,
    current_timestamp
)

from config import (
    SILVER_DB,
    GOLD_DB,
    SILVER_TABLE,
    GOLD_TABLE,
    S3_WAREHOUSE_PATH,
    PROCESSING_LOOKBACK_DAYS,
    SPARK_APP_NAME
)

# ---------------------------
# Spark Session
# ---------------------------
spark = (
    SparkSession.builder
    .appName(SPARK_APP_NAME)
    .config(
        "spark.sql.catalog.glue_catalog",
        "org.apache.iceberg.spark.SparkCatalog"
    )
    .config(
        "spark.sql.catalog.glue_catalog.warehouse",
        S3_WAREHOUSE_PATH
    )
    .config(
        "spark.sql.catalog.glue_catalog.catalog-impl",
        "org.apache.iceberg.aws.glue.GlueCatalog"
    )
    .config(
        "spark.sql.catalog.glue_catalog.io-impl",
        "org.apache.iceberg.aws.s3.S3FileIO"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# ---------------------------
# Read Silver Data
# ---------------------------
silver_df = spark.read.table(
    f"glue_catalog.{SILVER_DB}.{SILVER_TABLE}"
)

# ---------------------------
# Filter Processing Window
# ---------------------------
filtered_df = silver_df.filter(
    col("event_date") >= current_date() - expr(f"INTERVAL {PROCESSING_LOOKBACK_DAYS} DAYS")
)

# ---------------------------
# Aggregation
# ---------------------------
gold_df = (
    filtered_df
    .groupBy("event_date", "currency")
    .agg(
        count("event_id").alias("total_orders"),
        _sum("order_total").alias("total_revenue")
    )
    .withColumn(
        "avg_order_value",
        round(col("total_revenue") / col("total_orders"), 2)
    )
    .withColumnRenamed("event_date", "order_date")
)

# ---------------------------
# Write Gold Table (Overwrite)
# ---------------------------
(
    gold_df.writeTo(f"glue_catalog.{GOLD_DB}.{GOLD_TABLE}")
    .overwritePartitions()
)