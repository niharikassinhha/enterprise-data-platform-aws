AWS_REGION = "us-east-1"

SILVER_DB = "silver_dev"
GOLD_DB = "gold_dev"

SILVER_TABLE = "silver_order_created"
GOLD_TABLE = "gold_daily_order_metrics"

S3_WAREHOUSE_PATH = "s3://enterprise-data-platform-dev/"

# Rebuild window (supports backfills)
PROCESSING_LOOKBACK_DAYS = 30

SPARK_APP_NAME = "silver-to-gold-daily-order-metrics"