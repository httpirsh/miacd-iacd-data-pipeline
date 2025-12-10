FROM apache/spark:4.0.1

USER root

WORKDIR /app

# postgresql and pandas for data processing
RUN pip install --no-cache-dir pandas==2.3.3 psycopg2-binary==2.9.9

COPY consumer.py .

# download kafka connector and postgresql jdbc driver
CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,org.postgresql:postgresql:42.6.0", "consumer.py"]
