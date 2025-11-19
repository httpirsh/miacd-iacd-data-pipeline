"""
Kafka Producer for CO2 Emissions Data
Reads CSV file and streams data to Kafka topic
"""

import csv
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CO2DataProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='co2-raw'):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers: Kafka broker address
            topic: Kafka topic name
        """
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=1
        )
        logger.info(f"Kafka Producer initialized for topic: {topic}")

    def send_record(self, record, key=None):
        """
        Send a single record to Kafka
        
            record: Dictionary with data
            key: Optional partition key
        """
        try:
            future = self.producer.send(self.topic, value=record, key=key)
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            return True
        except KafkaError as e:
            logger.error(f"Failed to send record: {e}")
            return False

    def stream_csv(self, csv_file_path, delay=0.01, max_records=None):
        """
        Stream CSV data to Kafka
        
        Args:
            csv_file_path: Path to CSV file
            delay: Delay between records (seconds) to simulate streaming
            max_records: Maximum number of records to send (None = all)
        """
        logger.info(f"Starting to stream data from {csv_file_path}")
        
        records_sent = 0
        records_failed = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Use country-year as key for partitioning
                    key = f"{row.get('country', 'unknown')}_{row.get('year', '0')}"
                    
                    # Convert empty strings to None
                    record = {k: (v if v != '' else None) for k, v in row.items()}
                    
                    # Send to Kafka
                    if self.send_record(record, key=key):
                        records_sent += 1
                        if records_sent % 1000 == 0:
                            logger.info(f"Sent {records_sent} records...")
                    else:
                        records_failed += 1
                    
                    # Simulate streaming with delay
                    if delay > 0:
                        time.sleep(delay)
                    
                    # Check max records limit
                    if max_records and records_sent >= max_records:
                        logger.info(f"Reached max_records limit: {max_records}")
                        break
            
            # Flush remaining messages
            self.producer.flush()
            
            logger.info(f"Streaming completed!")
            logger.info(f"Records sent: {records_sent}")
            logger.info(f"Records failed: {records_failed}")
            
        except FileNotFoundError:
            logger.error(f"File not found: {csv_file_path}")
        except Exception as e:
            logger.error(f"Error streaming data: {e}")
        finally:
            self.close()

    def close(self):
        """Close the producer"""
        self.producer.close()
        logger.info("Producer closed")


def main():
    """Main function to run the producer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream CO2 data to Kafka')
    parser.add_argument('--csv', type=str, default='../owid-co2-data.csv',
                        help='Path to CSV file')
    parser.add_argument('--broker', type=str, default='localhost:9092',
                        help='Kafka broker address')
    parser.add_argument('--topic', type=str, default='co2-raw',
                        help='Kafka topic name')
    parser.add_argument('--delay', type=float, default=0.01,
                        help='Delay between records (seconds)')
    parser.add_argument('--max-records', type=int, default=None,
                        help='Maximum number of records to send')
    
    args = parser.parse_args()
    
    # Create producer and stream data
    producer = CO2DataProducer(
        bootstrap_servers=args.broker,
        topic=args.topic
    )
    
    producer.stream_csv(
        csv_file_path=args.csv,
        delay=args.delay,
        max_records=args.max_records
    )


if __name__ == '__main__':
    main()
