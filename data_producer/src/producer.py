from kafka import KafkaProducer
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        future.add_callback(on_send_success)
        future.add_errback(on_send_error)

        time.sleep(2)
    
if __name__ == "__main__":
    time.sleep(90)
    KAFKA_BROKER = 'kafka:9092'
    TOPIC = "transactions"
    producer = KafkaProducer(
    bootstrap_servers = KAFKA_BROKER,
    value_serializer = lambda v:json.dumps(v).encode('utf-8'),
    acks = 'all'
    )
    generate_transactions()
    
    