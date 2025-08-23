# Dots: JSON storage + queries + graph

A Python toolkit for JSON-based data storage, JSONiq-style queries (via optional RumbleDB), and directed graph analysis/visualization.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m dots.cli --help
```

### Storage

```bash
python -m dots.cli store ingest data/examples.json --id-field id
# With JSON Schema validation
python -m dots.cli store ingest data/examples.json --id-field id --schema scripts/example.schema.json
python -m dots.cli store list
```

### Query
- JSONiq (optional, requires Docker + RumbleDB)
- JMESPath fallback

```bash
python -m dots.cli query jmespath "[?type=='edge']"
# JSONiq (if Docker + RumbleDB available)
python -m dots.cli query jsoniq --file scripts/example.jq
```

### Graph

```bash
python -m dots.cli graph build --source-field source --target-field target --output graph.html
open graph.html  # macOS
```

## JSONiq via RumbleDB (optional)
1. Install Docker
2. Pull image: `docker pull rumbledb/rumble`
3. Run queries: `python -m dots.cli query jsoniq --file scripts/example.jq`

Data directory is `data/` by default. Override with `DOTS_DATA_DIR`.

## Spark (optional)
Docker Compose includes a Spark master and worker:

```bash
docker compose up -d spark-master spark-worker
# Spark master UI: http://localhost:8080
# Worker UI: http://localhost:8081
```
