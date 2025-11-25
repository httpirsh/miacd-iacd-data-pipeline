FROM apache/superset:latest

# Switch to root to install system packages
USER root

# Install PostgreSQL development packages (needed for psycopg2)
RUN apt-get update && \
    apt-get install -y libpq-dev gcc python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip in the venv, then install psycopg2-binary
# Using get-pip.py approach to install pip in venv
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python && \
    python -m pip install --no-cache-dir psycopg2-binary

# Verify installation
RUN python -c "import psycopg2; print('✅ psycopg2-binary installed successfully:', psycopg2.__version__)"

# Switch back to superset user for security
USER superset
