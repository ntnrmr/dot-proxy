FROM python:3.9-alpine

WORKDIR /app
COPY config.yaml .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

CMD ["python", "./main.py"]
