FROM apache/spark:4.0.1

USER root

WORKDIR /app

RUN pip install --no-cache-dir pandas==2.2.0 psycopg2-binary==2.9.9

COPY spark/consumer.py .

CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,org.postgresql:postgresql:42.6.0", "consumer.py"]
