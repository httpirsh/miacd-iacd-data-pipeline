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
            print(f"kafka broker not available (attempt {i+1}/10)...")
            time.sleep(5)
    
    raise Exception("could not connect to Kafka after several attempts")

dir_script = os.path.dirname(os.path.abspath(__file__))  # detect if is in container or local
# dir_script = '/app' (container) or '/caminho/projeto/kafka' (local)

dir_csv = os.path.join(dir_script, 'data', 'reduced_co2.csv')
# dir_csv = '/app/data/reduced_co2.csv' (container)

if not os.path.exists(dir_csv):  # se estiver em local! (mas não é suposto)
    dir_csv = os.path.join(os.path.dirname(dir_script), 'data', 'reduced_co2.csv')
    # dir_csv = '/caminho/projeto/kafka/data/reduced_co2.csv' (local)

df = pd.read_csv(dir_csv)
print(f"loaded {len(df)} records from {dir_csv}")

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
        
        print("finished dataset, restarting in 10 seconds")
        time.sleep(10)

except KeyboardInterrupt:
    print("producer interrupted by user")

finally:
    producer.close()