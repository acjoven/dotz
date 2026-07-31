FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dotz ./dotz
COPY data ./data
COPY scripts ./scripts

ENTRYPOINT ["python", "-m", "dotz.cli"]

