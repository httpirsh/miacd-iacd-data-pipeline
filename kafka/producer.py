import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import os

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def connect_kafka_producer():
    # Use 'kafka' for simple Zookeeper setup, 'kafka.default.svc.cluster.local' for KRaft
    kafka_broker = os.getenv('KAFKA_BROKER', 'kafka.default.svc.cluster.local:9092')
    
    for i in range(10):  # try up to 10 times
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_broker,
                value_serializer=json_serializer,
            )
            print(f" connected to Kafka at {kafka_broker}")
            return producer
        except NoBrokersAvailable:
            print(f"Kafka broker not available (attempt {i+1}/10)...")
            time.sleep(5)
    
    raise Exception("could not connect to Kafka after several attempts")

df = pd.read_csv('./data/reduced_co2.csv')

producer = connect_kafka_producer()

topic = 'emissions-topic'
print(f"starting to send to topic '{topic}'")

try:
    while True:
        for index, row in df.iterrows():
            message = row.to_dict()
            producer.send(topic, value=message)
            print(f"sent: {message.get('country', 'N/A')} - {message.get('year', 'N/A')}")
            time.sleep(0.03)
        
        print("finished dataset, restarting in 10 seconds...")
        time.sleep(10)
except KeyboardInterrupt:
    print("producer interrupted by user")
finally:
    producer.close()