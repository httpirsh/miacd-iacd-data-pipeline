dps apagar --

1. Kafka Producer
Lê um dataset de emissões de CO2 (ficheiro CSV)

Envia cada linha do dataset para um tópico Kafka (emissions-topic) em formato JSON

O producer está a funcionar e a enviar dados continuamente (em loop)

2. Spark Streaming
Consome os dados do tópico Kafka

Processa os dados em batches a cada 30 segundos

No código atual, está a fazer uma análise simples (debug) que inclui:

Contar o número de registos

Mostrar algumas estatísticas (média de CO2, etc.)

Mostrar os top 10 emissores de CO2

3. PostgreSQL
Configuramos uma base de dados PostgreSQL para armazenar os resultados do clustering

Criamos duas tabelas:

co2_clusters: para armazenar os resultados do clustering por país

cluster_stats: para armazenar estatísticas agregadas por cluster

Também criamos uma view cluster_analysis para facilitar a análise

Inserimos um registo de exemplo para teste


---

Tabela co2_clusters
- id: Chave primária
- batch_id: ID do batch de processamento (útil para acompanhar o streaming)
- country: Nome do país
- iso_code: Código ISO do país
- avg_co2: Média de emissões de CO2 (em milhões de toneladas) para o país no período analisado
- avg_co2_per_capita: Média de emissões per capita
- avg_gdp: Média do PIB
- avg_population: Média da população
- cluster: Cluster atribuído pelo algoritmo K-means
- processing_time: Timestamp do processamento

Tabela cluster_stats
- id: Chave primária
- batch_id: ID do batch
- cluster: Número do cluster
- num_countries: Número de países no cluster
- avg_co2_cluster: Média de CO2 do cluster
- avg_co2_per_capita_cluster: Média de CO2 per capita do cluster
- avg_gdp_cluster: Média do PIB do cluster
- processing_time: Timestamp

View cluster_analysis
- Agrega os dados da tabela co2_clusters por cluster, mostrando:
- Número de países
- Médias de CO2, CO2 per capita e PIB

---
Como verificar o estado atual?
Kafka Producer: docker-compose logs producer - deve mostrar os países a serem enviados

Spark: docker-compose logs spark - deve mostrar os batches a serem processados e as estatísticas

PostgreSQL: Pode usar o pgAdmin (http://localhost:5050) ou o comando psql para ver as tabelas

---

Dataset CO₂ → Kafka Producer → Kafka Broker → Spark Streaming → PostgreSQL → (Próximo: Superset)

---

objetivo do projeto:
Criar um pipeline de dados em tempo real para:
- Analisar emissões de CO₂ por país
- Agrupar países por padrões de emissões (clustering)
- Visualizar os resultados em dashboards

---
💡 Para Saber Mais:
Documentação PostgreSQL: https://www.postgresql.org/docs/

Spark + PostgreSQL: https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html

Docker Compose: https://docs.docker.com/compose/

