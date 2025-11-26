Enunciado do Projeto Prático
Ano Letivo: 2025/2026
Data de Lançamento: 12 de Novembro de 2025
Docente: Pedro Neves
1. Objetivo Geral
O objetivo deste projeto é desenhar, implementar e simular um pipeline de engenharia de dados do mundo real ("end-to-end"), utilizando contentores Docker e orquestração via Kubernetes.
Os alunos devem demonstrar a capacidade de integrar ingestão de dados, armazenamento, processamento distribuído e visualização numa infraestrutura escalável.
2. Arquitetura e Componentes do Pipeline
O sistema deve ser implementado sobre o Minikube (ambiente Kubernetes local) ou, opcionalmente para equipas avançadas, num cluster Kubernetes na cloud. O pipeline deve incluir os seguintes componentes:
Ingestão de Dados: Utilização de ferramentas como Apache Kafka ou Apache Spark para capturar dados.
Armazenamento de Dados: Persistência dos dados brutos ou processados utilizando bases de dados (ex: Postgres, MongoDB) ou object storage (ex: MinIO). O uso de armazenamento distribuído (HDFS) é opcional.
Motor de Processamento: Utilização do Apache Spark para processar, transformar e analisar os dados.
Visualização (Opcional/Recomendado): Criação de dashboards para apresentação de <i>insights</i> (ex: Grafana, Superset).
Monitorização (Opcional): Monitorização da infraestrutura (ex: Prometheus, Grafana).
3. Cenários e Datasets Sugeridos
As equipas devem escolher um domínio de aplicação. Abaixo seguem sugestões e fontes de dados abertos:
Smart City / IoT:
Deteção de tráfego em tempo real, qualidade do ar ou consumo energético.
Fontes: Portal de Dados Abertos de Lisboa, Transport for London API.
Clima e Ambiente:
Análise de tendências de temperatura, previsão de eventos extremos ou emissões de CO₂.
Fontes: NOAA Climate Data, NASA EarthData, Our World in Data.
Redes Sociais e Análise de Sentimento:
Análise de sentimento em tempo real (ex: Twitter/X, Reddit) sobre eventos ou produtos.
Fontes: Kaggle (Twitter US Airline Sentiment), Reddit Comments, News API.
Saúde e Ciências da Vida:
Padrões de propagação de doenças, readmissão de pacientes ou clustering genético.
Fontes: WHO Global Health Observatory, UCI Machine Learning Repository, Datasets COVID-19.
Finanças e Deteção de Fraude:
Deteção de fraude em transações, tendências de bolsa ou modelação de risco.
Fontes: Kaggle (Credit Card Fraud), Yahoo Finance API, Banco Mundial.
4. Entregáveis
O projeto consiste nas seguintes entregas:
Proposta de Projeto (1 Slide):
Título e equipa.
Problema/Objetivo (o que o projeto visa demonstrar).
Dataset (fonte, tipo e tamanho aproximado).
Arquitetura Proposta (diagrama de fluxo de dados).
Tecnologias/Ferramentas a usar.
Ficheiros de Deployment:
Todo o código necessário para reproduzir o ambiente (Dockerfiles, manifestos Kubernetes, scripts de jobs Spark, etc.).
Relatório Técnico (Máx. 5 páginas):
Descrição do problema, arquitetura detalhada, tecnologias usadas, desafios de design e avaliação dos resultados.
Apresentação e Demonstração:
Apresentação de 10 a 15 minutos seguida de Q&A.
Demonstração do pipeline a funcionar ao vivo e apresentação dos insights obtidos.
5. Calendário e Prazos
Submissão da Proposta: 14 de Novembro de 2025 (via InforDocente).
Submissão Final do Projeto: 11 de Dezembro de 2025 (via InforDocente).
Apresentações e Demos: 12 e 19 de Dezembro de 2025 (durante as aulas).
6. Critérios de Avaliação
A nota final do projeto será distribuída da seguinte forma:
30% - Implementação Técnica: Sistema funcional e reprodutível utilizando tecnologias distribuídas apropriadas (Docker, K8s, Spark).
30% - Tratamento de Dados e Analytics: Eficácia na ingestão, transformação, armazenamento e pipeline de análise de dados.
15% - Relatório Técnico: Clareza, estrutura e profundidade (definição do problema, escolhas de design, desafios, resultados).
15% - Apresentação e Comunicação: Clareza na demonstração, capacidade de explicar aspetos técnicos e resultados.
10% - Qualidade da Arquitetura e Design: Decisões arquiteturais, escalabilidade e integração limpa dos componentes.