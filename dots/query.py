from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, List, Tuple

import jmespath


def run_jmespath(expression: str, documents: List[dict]) -> Any:
    compiled = jmespath.compile(expression)
    return compiled.search(documents)


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def run_jsoniq(query_text: str, data_dir: Path) -> Tuple[bool, str]:
    if not _docker_available():
        return False, "Docker is not installed or not on PATH."
    # Attempt RumbleDB container execution. This is a best-effort wrapper and may need adjustment.
    # Expose data_dir to /data inside the container.
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{str(data_dir.resolve())}:/data:ro",
        "rumbledb/rumble",
        "--shell",
    ]
    try:
        proc = subprocess.run(cmd, input=query_text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if proc.returncode == 0:
            return True, proc.stdout.decode("utf-8")
        return False, proc.stderr.decode("utf-8")
    except Exception as exc:
        return False, str(exc)
