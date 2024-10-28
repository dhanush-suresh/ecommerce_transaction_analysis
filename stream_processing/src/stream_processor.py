from kafka import KafkaConsumer
import json
from collections import defaultdict
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_BROKER = 'kafka:9092'
CONSUME_TOPIC = 'transactions'
PRODUCE_TOPIC = 'product-sales'

sales_aggregate = defaultdict(int)

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

def process_transaction(transaction):
    try:
        product_id = transaction['product_id']
        quantity = transaction['quantity']
        sales_aggregate[product_id] += quantity
        logger.info(f"Processed: {transaction}")
        logger.info(f"Total Sales for {product_id}: {sales_aggregate[product_id]}")
    except KeyError as e:
        logger.error(f"Missing key in transaction: {e}")
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")

def process_transactions(consumer):
    try:
        for message in consumer:
            try:
                transaction = message.value
                process_transaction(transaction)
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
    try:
        logger.info("Starting transaction processor")
        consumer = create_consumer()
        process_transactions(consumer)
    except Exception as e:
        logger.critical(f"Critical error in main program: {e}")
        sys.exit(1)