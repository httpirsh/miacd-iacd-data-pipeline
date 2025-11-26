1. Docker (Módulos 2, 3, 4, 5)
Comandos de Ciclo de Vida de Contentores
Gerir a execução de contentores.
Criar e iniciar um contentor:
code
Bash
# Sintaxe básica
docker run <imagem>

# Com mapeamento de portas (Host:Contentor) e em background (detached)
docker run -p 3000:80 -d --name meu-contentor <imagem>

# Interativo (terminal)
docker run -it <imagem>

# Limpar automaticamente ao parar
docker run --rm <imagem>
Listar contentores:
code
Bash
docker ps           # Apenas em execução
docker ps -a        # Todos (incluindo parados)
Parar e Remover:
code
Bash
docker stop <container-id>   # Parar graciosamente
docker kill <container-id>   # Forçar paragem
docker rm <container-id>     # Remover contentor (deve estar parado)
docker container prune       # Remover todos os contentores parados
Interagir com contentores em execução:
code
Bash
docker attach <container-id> # Acoplar ao terminal do contentor
docker logs <container-id>   # Ver logs (output)
Imagens (Dockerfiles e Gestão)
Criar e gerir as "blueprints" dos contentores.
Estrutura Básica de um Dockerfile:
code
Dockerfile
# Imagem base
FROM node 

# Diretoria de trabalho
WORKDIR /app

# Copiar ficheiros (Host -> Imagem)
COPY package.json .

# Instalar dependências
RUN npm install

# Copiar código fonte (após dependências para otimizar cache)
COPY . .

# Expor porta (documentação)
EXPOSE 80

# Comando de arranque
CMD ["node", "server.js"]
Construir (Build) e Gerir Imagens:
code
Bash
# Construir imagem a partir do Dockerfile na diretoria atual (.)
docker build -t <nome-imagem> .

# Listar imagens
docker images

# Inspecionar detalhes
docker image inspect <image-id>

# Remover imagem
docker rmi <image-id>
docker image prune
Docker Hub (Partilha):
code
Bash
docker login
docker push <docker-hub-id>/<nome-imagem>
docker pull <docker-hub-id>/<nome-imagem>
Volumes (Persistência de Dados)
code
Bash
# Criar um volume nomeado ao iniciar o contentor
docker run -v <nome-volume>:<caminho-no-contentor> <imagem>

# Listar volumes
docker volume ls
Networking
code
Bash
# Criar uma rede
docker network create <nome-rede>

# Iniciar contentor numa rede específica
docker run --network <nome-rede> <imagem>
2. Docker Compose (Módulo 6)
Ferramenta para orquestrar aplicações multi-contentor.
Exemplo de docker-compose.yaml:
code
Yaml
version: "3.8"
services:
  mongodb:
    image: mongo:4.4.6
    volumes:
      - data:/data/db
  
  node-webapp:
    build: ./
    ports:
      - "3000:3000"
    depends_on:
      - mongodb
    volumes:
       - logs:/app/logs

volumes:
  data:
  logs:
Comandos Compose:
code
Bash
docker-compose up -d    # Iniciar tudo em background
docker-compose down     # Parar e remover tudo
3. Kubernetes (Módulos 7, 8, 9, 10)
Comandos Básicos (Kubectl & Minikube)
code
Bash
# Aplicar uma configuração (criar/atualizar recursos)
kubectl apply -f <ficheiro-config.yaml>

# Obter estado dos recursos
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get pvc

# Eliminar recursos
kubectl delete -f <ficheiro-config.yaml>

# Aceder a um serviço no Minikube (local)
minikube service <nome-servico>
Estrutura dos Ficheiros YAML (Objetos K8s)
Deployment (Gerir Pods):
code
Yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: users-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: users
  template:
    metadata:
      labels:
        app: users
    spec:
      containers:
        - name: kubs-users
          image: pedromneves/kubs-users-img
          ports:
            - containerPort: 8080
Service (Networking/Exposição):
code
Yaml
apiVersion: v1
kind: Service
metadata:
  name: users-service
spec:
  selector:
    app: users
  type: LoadBalancer  # ou ClusterIP, NodePort
  ports:
    - protocol: TCP
      port: 8080        # Porta exposta
      targetPort: 8080  # Porta do contentor
Persistent Volume Claim (Volumes):
code
Yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: host-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
(Nota: Para ligar o volume, adiciona-se volumes e volumeMounts no spec do Deployment).
Service Discovery (DNS):
Dentro do cluster, os Pods comunicam usando o nome do serviço:
http://<nome-do-servico>.default
4. Kafka (Módulo 11)
Plataforma de transporte de dados distribuída.
Iniciar a infraestrutura (nos binários):
code
Bash
# Iniciar Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Iniciar Kafka Broker
bin/kafka-server-start.sh config/server.properties

# Iniciar Kafka Manager (CMAK)
bin/cmak -Dconfig.file=conf/application.conf
Gestão de Tópicos (CLI):
code
Bash
# Criar Tópico
bin/kafka-topics.sh --create --topic first_topic --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092
Produtor (Producer) CLI:
code
Bash
bin/kafka-console-producer.sh --topic first_topic --bootstrap-server localhost:9092
Consumidor (Consumer) CLI:
code
Bash
bin/kafka-console-consumer.sh --topic first_topic --from-beginning --bootstrap-server localhost:9092
5. Apache Spark (Módulo 13)
Processamento de Big Data. Código em Python (PySpark).
Configuração Inicial:
code
Python
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("MyJob")
sc = SparkContext(conf = conf)
Criação de RDDs:
code
Python
# Carregar ficheiro de texto
lines = sc.textFile("dados.txt")
Transformações (Transformations - Lazy):
code
Python
# Map: Transformar cada elemento
rdd2 = rdd1.map(lambda x: x * 2)

# FlatMap: Produzir múltiplos valores para um input (ex: split palavras)
words = lines.flatMap(lambda x: x.split(" "))

# Filter: Manter apenas o que cumpre a condição
errors = lines.filter(lambda x: "ERROR" in x)

# ReduceByKey (Agregação por chave)
totals = rdd_kv.reduceByKey(lambda x, y: x + y)

# SortByKey
sorted_rdd = rdd_kv.sortByKey()
Ações (Actions - Trigger Execution):
code
Python
# Contar elementos
count = rdd.count()

# Trazer resultados para o driver (cuidado com tamanho!)
results = rdd.collect()

# Contar ocorrências de valores únicos
counts = rdd.countByValue()
Submeter Job:
code
Bash
spark-submit script.py