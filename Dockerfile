FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dots ./dots
COPY data ./data
COPY scripts ./scripts

ENTRYPOINT ["python", "-m", "dots.cli"]

