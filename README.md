# Dotz: JSON storage + queries + graph

A Python toolkit for JSON-based data storage, JSONiq-style queries (via optional RumbleDB), and directed graph analysis/visualization.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m dotz.cli --help
```

### Storage

```bash
python -m dotz.cli store ingest data/examples.json --id-field id
# With JSON Schema validation
python -m dotz.cli store ingest data/examples.json --id-field id --schema scripts/example.schema.json
python -m dotz.cli store list
```

### Query
- JSONiq (optional, requires Docker + RumbleDB)
- JMESPath fallback

```bash
python -m dotz.cli query jmespath "[?type=='edge']"
# JSONiq (if Docker + RumbleDB available)
python -m dotz.cli query jsoniq --file scripts/example.jq
```

### Graph

```bash
python -m dotz.cli graph build --source-field source --target-field target --output graph.html
open graph.html  # macOS
```

## JSONiq via RumbleDB (optional)
1. Install Docker
2. Pull image: `docker pull rumbledb/rumble`
3. Run queries: `python -m dotz.cli query jsoniq --file scripts/example.jq`

Data directory is `data/` by default. Override with `DOTZ_DATA_DIR`.

## Spark (optional)
Docker Compose includes a Spark master and worker:

```bash
docker compose up -d spark-master spark-worker
# Spark master UI: http://localhost:8080
# Worker UI: http://localhost:8081
```

Example PySpark job (uses files in `data/`):

```bash
# Ensure Spark is up (see above) and venv is active
export SPARK_MASTER_URL=spark://localhost:7077
python scripts/spark_example.py
```

## Hadoop (optional)
Compose also provides HDFS (NameNode/DataNode) for larger datasets:

```bash
docker compose up -d hadoop-namenode hadoop-datanode
# NameNode UI: http://localhost:9870

# Example: put local data/ JSON files into HDFS (requires Hadoop client or exec into container)
docker exec -it hadoop-namenode hdfs dfs -mkdir -p /user/dotz/data
docker exec -it hadoop-namenode hdfs dfs -put /host_data/*.json /user/dotz/data/

# Run PySpark example reading from HDFS
export DOTZ_HDFS_GLOB=hdfs://hadoop-namenode:8020/user/dotz/data/*.json
export SPARK_MASTER_URL=spark://localhost:7077
python scripts/spark_example.py
```
