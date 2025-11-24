FROM apache/spark:4.0.1

USER root

WORKDIR /app

# Instalar dependências Python
# A imagem oficial já tem Python, mas precisamos instalar as libs do projeto
RUN pip install --no-cache-dir pandas==2.2.0 psycopg2-binary==2.9.9

# Copiar o consumer
COPY spark/consumer.py .

# Executar usando spark-submit (padrão do Spark)
# Adicionamos os pacotes do Kafka e Postgres
# Nota: Usamos a versão Scala 2.13 do conector Kafka, pois Spark 4.x geralmente usa Scala 2.13
CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,org.postgresql:postgresql:42.6.0", "consumer.py"]
