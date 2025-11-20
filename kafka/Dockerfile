FROM python:3
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY producer_v2.py .
CMD ["python", "producer_v2.py"]