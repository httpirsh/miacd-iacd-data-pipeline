FROM apache/superset:latest

USER root

# postgresql driver dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install postgresql driver (psycopg2)
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python && \
    python -m pip install --no-cache-dir psycopg2-binary

USER superset
