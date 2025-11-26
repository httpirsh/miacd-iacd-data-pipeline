Manual Teórico: Infraestruturas Avançadas para Data Science
Módulo 1: Fundamentos e Paradigmas
O curso começa por estabelecer que a Ciência de Dados moderna não é apenas sobre algoritmos e modelos, mas sim sobre pipelines completos (Ingestão 
→
→
 Armazenamento 
→
→
 Processamento 
→
→
 Análise 
→
→
 Deployment).
O Problema da Escala: Scripts que correm num portátil não funcionam quando os dados crescem para Terabytes ou Petabytes. É necessário mudar de uma abordagem Scale-Up (Vertical: máquina mais potente) para Scale-Out (Horizontal: cluster de máquinas).
Paradigmas de Infraestrutura:
Monolítico/On-Prem: Servidores físicos. Difícil de escalar e gerir.
Cluster/Distribuído: (ex: Hadoop). Permite processar Big Data dividindo o trabalho.
Cloud: Recursos on-demand e elásticos (AWS, Azure).
Cloud Native: O foco atual do curso. Uso de Contentores e Orquestração para criar aplicações portáteis, escaláveis e resilientes.
Módulos 2-6: O Mundo dos Contentores (Docker)
1. O que é um Contentor?
É uma unidade de software padronizada. Ao contrário de uma Máquina Virtual (VM) que virtualiza o hardware e precisa de um Sistema Operativo completo (pesado), o contentor virtualiza o Sistema Operativo.
Vantagem: É leve, arranca em segundos e garante que a aplicação corre igual em qualquer lugar ("It works on my machine" deixa de ser um problema).
Isolamento: Usa funcionalidades do Linux (Namespaces e Cgroups) para garantir que um processo não interfere com outro.
2. Imagens vs. Contentores
Imagem: É a "forma" ou o "blueprint". É read-only (apenas leitura) e construída por camadas (layers). Se mudares o código, tens de reconstruir a imagem.
Contentor: É a instância em execução da imagem. É efémero (temporário). Quando apagas o contentor, os dados lá dentro desaparecem (a menos que uses volumes).
3. Persistência de Dados (Volumes)
Como os contentores são efémeros, para guardar dados (ex: base de dados), usamos Volumes. Os volumes são pastas no computador host que são montadas dentro do contentor, sobrevivendo à destruição do mesmo.
4. Networking e Docker Compose
Por defeito, os contentores são isolados. Para comunicar com o mundo exterior, é preciso fazer Port Mapping (mapear porta do host para a porta do contentor).
Docker Compose: É uma ferramenta para definir e correr aplicações multi-contentor (ex: uma App Python + Base de Dados Mongo). Em vez de correr muitos comandos manuais, define-se tudo num ficheiro yaml e o Docker cria a rede e arranca os serviços na ordem certa.
Módulos 7-10: Orquestração Automatizada (Kubernetes)
Quando passamos de 5 contentores para 500, o Docker sozinho não chega. Precisamos de um Orquestrador. O padrão da indústria é o Kubernetes (K8s).
1. Abordagem Declarativa
No K8s, não dizes "arranca este contentor". Tu declaras um estado desejado (ex: "quero 3 réplicas da API de utilizadores"). O K8s monitoriza o cluster e trabalha continuamente para manter esse estado (se um nó falhar, ele recria os contentores noutro sítio).
2. Objetos Principais do K8s
Pod: A unidade atómica. Normalmente contém um contentor (mas pode ter mais se forem muito acoplados). Os Pods são mortais (têm um ciclo de vida curto).
Deployment: Gere os Pods. É aqui que defines quantas réplicas queres e qual a imagem a usar. Permite rollbacks e updates sem downtime.
Service: Como os Pods morrem e mudam de IP, o Service fornece um endereço de rede estável (IP fixo e DNS) para aceder a um grupo de Pods. Tipos:
ClusterIP: Apenas interno.
NodePort: Abre uma porta em cada nó do cluster.
LoadBalancer: Usa um balanceador de carga externo (nuvem) para expor o serviço.
Persistent Volume (PV) & Claim (PVC): O sistema de armazenamento do K8s. O PVC é um "pedido" de armazenamento que o Pod faz, e o PV é o recurso real (disco).
Módulo 11: Transporte de Dados (Apache Kafka)
Numa arquitetura distribuída, os dados precisam de se mover entre sistemas (Producers 
→
→
 Consumers) de forma fiável e rápida.
O que é: Uma plataforma de streaming distribuída.
Conceitos Chave:
Topic: Uma categoria onde os dados são guardados (ex: "transacoes-bancarias").
Producer: Quem envia os dados.
Consumer: Quem lê os dados.
Broker: Os servidores que compõem o cluster Kafka.
Escalabilidade e Tolerância a Falhas:
Os tópicos são divididos em Partições. Isso permite paralelizar a leitura e escrita.
As partições têm Réplicas espalhadas pelos Brokers. Se um servidor falhar, os dados não se perdem.
Módulo 13: Processamento de Big Data (Apache Spark)
Para processar grandes volumes de dados, o Hadoop MapReduce era lento porque escrevia tudo em disco. O Spark revolucionou isto ao fazer o processamento in-memory (na RAM), sendo até 100x mais rápido.
1. Arquitetura
Driver Program: O "cérebro" que define o que fazer.
Cluster Manager: Gere os recursos (pode ser YARN, Mesos ou o próprio do Spark).
Executors: Os "operários" nos nós que executam as tarefas e guardam dados.
2. RDD (Resilient Distributed Dataset)
É a principal abstração de dados do Spark.
Imutável: Não podes alterar um RDD, crias um novo a partir de uma transformação.
Distribuído: Os dados estão partidos por vários nós.
Lazy Evaluation (Preguiçoso): O Spark não executa nada até que uma ação seja pedida. Ele apenas constrói um plano de execução (DAG).
3. Operações
Transformações: Criam novos RDDs (ex: map, filter, flatMap).
Ações: Devolvem um resultado ao Driver ou escrevem em disco (ex: count, collect, saveAsTextFile). Só aqui é que o processamento acontece realmente.