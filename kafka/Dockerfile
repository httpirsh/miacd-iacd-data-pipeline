FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
RUN pip install --no-cache-dir kafka-python-ng==2.2.3 pandas==2.2.0

# Copiar o producer (caminho relativo ao contexto raiz)
COPY kafka/producer.py .

# Copiar dados da pasta raiz do projeto
COPY data/reduced_co2.csv ./data/reduced_co2.csv

# Executar producer
CMD ["python", "producer.py"]
