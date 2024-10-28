from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers = 'localhost:9092',
    value_serializer = lambda v:json.dumps(v).encode('utf-8')
)

def generate_transactions():
    return{
        'order_id' : str(random.randint(1000,99999)),
        'user_id' : 'user_' + str(random.randint(1,9999)),
        'product_id' : 'product_' + str(random.randint(1,50)),
        'quantity' : random.randint(1,5),
        'price': round(random.uniform(10,100.0),2),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
while True:
    transaction = generate_transactions()
    producer.send('transactions',transaction)
    print(f"Sent: {transaction}")
    time.sleep(1)