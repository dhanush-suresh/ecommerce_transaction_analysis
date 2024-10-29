from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import fastavro
import io

# Define your Avro schema
avro_schema = {
    "type": "record",
    "name": "Transaction",
    "fields": [
        {"name": "order_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "product_id", "type": "string"},
        {"name": "quantity", "type": "int"},
        {"name": "price", "type": "float"},
        {"name": "timestamp", "type": "string"}
    ]
}

# Define a UDF to deserialize Avro data
@udf(returnType=StructType([
    StructField("order_id", StringType()),
    StructField("user_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity", IntegerType()),
    StructField("price", FloatType()),
    StructField("timestamp", StringType())
]))
def deserialize_avro(avro_bytes):
    bytes_io = io.BytesIO(avro_bytes)
    reader = fastavro.schemaless_reader(bytes_io, avro_schema)
    return (reader['order_id'], reader['user_id'], reader['product_id'], 
            reader['quantity'], reader['price'], reader['timestamp'])


# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaAvroConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "transactions") \
    .load()

# Deserialize Avro data
deserialized_df = df.select(deserialize_avro(df.value).alias("data")) \
    .select("data.*")

# Print the result to console
query = deserialized_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()