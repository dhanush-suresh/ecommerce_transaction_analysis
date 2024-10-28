from kafka import KafkaConsumer
import json
from collections import defaultdict
from cassandra.cluster import Cluster
import logging
import sys
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_BROKER = 'kafka:9092'
CONSUME_TOPIC = 'transactions'

CASSANDRA_KEYSPACE = 'ecommerce'
CASSANDRA_TABLE = 'product_sales'

sales_aggregate = defaultdict(int)



# Prepare the insert statement

def create_keyspace(session):
    session.execute(f"""CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} 
                    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}""")

def create_table(session):
    session.execute(f"""
    CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
        order_id TEXT PRIMARY KEY,
        product_id TEXT,
        user_id TEXT,
        quantity INT,
        price DOUBLE,
        timestamp TIMESTAMP
    )
    """)

def create_consumer():
    try:
        consumer = KafkaConsumer(
            CONSUME_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='transaction-processor'
        )
        logger.info("Kafka consumer created successfully")
        return consumer
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        sys.exit(1)

def process_transaction(transaction,session):
    insert_stmt = session.prepare(
    f"INSERT INTO {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (order_id,product_id,user_id,quantity,price, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
)
    try:
        order_id = transaction['order_id']
        product_id = transaction['product_id']
        user_id = transaction['user_id']
        quantity = transaction['quantity']
        price = transaction['price']
        timestamp_str = transaction['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        session.execute(insert_stmt, (order_id,product_id, user_id,quantity,price,timestamp))
        logger.info(f"Processed: {transaction}")
    except KeyError as e:
        logger.error(f"Missing key in transaction: {e}")
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        

def process_transactions(consumer,session):
    try:
        for message in consumer:
            try:
                transaction = message.value
                process_transaction(transaction,session)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode message: {message.value}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error in message consumption loop: {e}")
    finally:
        try:
            consumer.close()
            logger.info("Consumer closed successfully")
        except Exception as e:
            logger.error(f"Error closing consumer: {e}")

if __name__ == "__main__":
    time.sleep(90)
    logger.info("Processor Starting")    
    try:
        cluster = Cluster(['cassandra'])
        session = cluster.connect()
        create_keyspace(session)
        create_table(session)
        logger.info("Starting transaction processor")
        consumer = create_consumer()
        process_transactions(consumer,session)
    except Exception as e:
        logger.critical(f"Critical error in main program: {e}")
        sys.exit(1)