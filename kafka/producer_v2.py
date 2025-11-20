import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time

#  json serialization method
def json_serializer(data):
    return json.dumps(data).encode("utf-8")

"""
def connect_kafka_producer():
    producerr = None
    while producerr is None:
        try:
            producerr = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=json_serializer
            )
            print("Conectado ao Kafka com sucesso!")
        except NoBrokersAvailable:
            print("waiting for kafka broker")
            time.sleep(5)  
    return producerr

producer = connect_kafka_producer()
"""
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=json_serializer
)


#df = pd.read_csv('./data/reduced_co2.csv')
df = pd.read_csv('/app/data/reduced_co2.csv')

TOPIC_NAME = 'emissions-topic'
print(f"initing data sending to topic '{TOPIC_NAME}'")
print("press ctrl+c to stop the producer")

try:
    while True:
        for index, row in df.iterrows():
            message = row.to_dict() # each row of df as a dict
            producer.send(TOPIC_NAME, value=message)  # send the msg data to topic
            
            # our feedback
            print(f"sended: {message['country']} - {message['year']}")
            
            time.sleep(0.5) # half second
    
        print("end of dataset, restarting...")
        time.sleep(10)  # wait 10 seconds before restarting the dataset sending
except KeyboardInterrupt:
    print("producer stopped")
finally:
    producer.close()