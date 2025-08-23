from __future__ import annotations

import json
import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def main() -> None:
    master_url = os.getenv("SPARK_MASTER_URL", "spark://localhost:7077")
    data_dir = Path(os.getenv("DOTS_DATA_DIR", Path.cwd() / "data"))

    spark = (
        SparkSession.builder
        .appName("dots-spark-example")
        .master(master_url)
        .getOrCreate()
    )

    # Read all JSON docs in data_dir (documents are individual JSON files)
    df = spark.read.json(str(data_dir / "*.json"))
    print(f"Total docs: {df.count()}")

    # Edge-only view and simple aggregation
    edges = df.where(col("type") == "edge")
    print(f"Edge count: {edges.count()}")

    # Compute out-degree by source
    out_degree = edges.groupBy("source").count().orderBy(col("count").desc())
    out_rows = [r.asDict(recursive=True) for r in out_degree.collect()]
    print(json.dumps({"out_degree": out_rows}, ensure_ascii=False, indent=2))

    spark.stop()


if __name__ == "__main__":
    main()


