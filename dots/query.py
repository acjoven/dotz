from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, List, Tuple
import tempfile

import jmespath


def run_jmespath(expression: str, documents: List[dict]) -> Any:
    compiled = jmespath.compile(expression)
    return compiled.search(documents)


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def run_jsoniq(query_text: str, data_dir: Path) -> Tuple[bool, str]:
    if not _docker_available():
        return False, "Docker is not installed or not on PATH."
    try:
        # Write the query to a temporary file and mount it read-only for RumbleDB
        with tempfile.TemporaryDirectory() as tmpdir:
            query_dir = Path(tmpdir)
            query_file = query_dir / "query.jq"
            query_file.write_text(query_text, encoding="utf-8")

            cmd_query_path = [
                "docker", "run", "--rm",
                "-v", f"{str(data_dir.resolve())}:/data:ro",
                "-v", f"{str(query_dir)}:/queries:ro",
                "rumbledb/rumble",
                "--query-path", "/queries/query.jq",
            ]
            proc = subprocess.run(cmd_query_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            if proc.returncode == 0:
                return True, proc.stdout.decode("utf-8")

            # Fallback: try --shell with explicit boolean value
            # cmd_shell = [
                # "docker", "run", "--rm",
                # "-v", f"{str(data_dir.resolve())}:/data:ro",
                # "rumbledb/rumble",
                # "--shell", "yes",
            # ]
            # proc2 = subprocess.run(cmd_shell, input=query_text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            # if proc2.returncode == 0:
                # return True, proc2.stdout.decode("utf-8")
            return False, proc.stderr.decode("utf-8") # + "\n" + proc2.stderr.decode("utf-8")
    except Exception as exc:
        return False, str(exc)
