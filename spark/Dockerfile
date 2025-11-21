FROM python:3.9-slim-bullseye

# Instalar Java 11 (versão compatível com Debian bullseye)
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Definir JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Instalar PySpark e dependências
RUN pip install --no-cache-dir \
    pyspark==3.4.1 \
    kafka-python==2.0.2 \
    pandas==2.0.3

# Criar diretório de trabalho
WORKDIR /app

# Copiar ficheiros
COPY consumer.py .

# Configurar diretório de checkpoints
RUN mkdir -p /tmp/checkpoints && chmod 777 /tmp/checkpoints

# Comando para executar o consumer
CMD ["spark-submit", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", \
    "--conf", "spark.sql.adaptive.enabled=true", \
    "--conf", "spark.sql.adaptive.coalescePartitions.enabled=true", \
    "--conf", "spark.streaming.kafka.maxRatePerPartition=100", \
    "--conf", "spark.driver.memory=2g", \
    "--conf", "spark.executor.memory=2g", \
    "/app/consumer_v2.py"]