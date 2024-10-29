from kafka import KafkaProducer
import json
import time
import random
import logging
import io
from avro import schema, io as avro_io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

avro_schema_dict = {
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

avro_schema = schema.parse(json.dumps(avro_schema_dict))

def avro_encoder(data):
    bytes_writer = io.BytesIO()
    encoder = avro_io.BinaryEncoder(bytes_writer)
    writer = avro_io.DatumWriter(avro_schema)
    writer.write(data, encoder)
    return bytes_writer.getvalue()

def on_send_error(excp):
    logger.error(f"Error sending message: {excp}")

def on_send_success(record_metadata):
    logger.info(f"Message sent successfully. Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
    
def generate_transactions():
    while True:
        transaction = {
        'order_id' : str(random.randint(1000,99999)),
        'user_id' : 'user_' + str(random.randint(1,9999)),
        'product_id' : 'product_' + str(random.randint(1,50)),
        'quantity' : random.randint(1,5),
        'price': round(random.uniform(10,100.0),2),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        future = producer.send(TOPIC, transaction)
        future.get(timeout=10)
        future.add_callback(on_send_success)
        future.add_errback(on_send_error)

        time.sleep(2)
    
if __name__ == "__main__":
    KAFKA_BROKER = 'kafka:9092'
    TOPIC = "transactions"
    producer = KafkaProducer(
    bootstrap_servers = KAFKA_BROKER,
    value_serializer = avro_encoder,
    acks = 'all'
    )
    generate_transactions()
    
    