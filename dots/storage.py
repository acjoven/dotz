from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional
from jsonschema import validate as jsonschema_validate, ValidationError


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_data_dir() -> Path:
    env_dir = os.getenv("DOTS_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd() / "data"


@dataclass
class JsonStorage:
    data_dir: Path

    @classmethod
    def create(cls, data_dir: Optional[Path] = None) -> "JsonStorage":
        directory = data_dir or _default_data_dir()
        directory.mkdir(parents=True, exist_ok=True)
        return cls(data_dir=directory)

    def _path_for_id(self, doc_id: str) -> Path:
        return self.data_dir / f"{doc_id}.json"

    def ingest(self, source_path: Path, id_field: Optional[str] = None, schema: Optional[dict] = None) -> List[str]:
        text = Path(source_path).read_text(encoding="utf-8")
        try:
            data = json.loads(text)
            records: Iterable[Any]
            if isinstance(data, list):
                records = data
            else:
                records = [data]
        except json.JSONDecodeError:
            # Try JSON Lines
            records = [json.loads(line) for line in text.splitlines() if line.strip()]

        ids: List[str] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            if schema is not None:
                try:
                    jsonschema_validate(instance=record, schema=schema)
                except ValidationError:
                    # Skip invalid records
                    continue
            doc_id = str(record.get(id_field)) if id_field and record.get(id_field) is not None else str(uuid.uuid4())
            path = self._path_for_id(doc_id)
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            ids.append(doc_id)
        return ids

    def list_ids(self) -> List[str]:
        return sorted(p.stem for p in self.data_dir.glob("*.json"))

    def load_all(self) -> List[dict]:
        docs = []
        for p in self.data_dir.glob("*.json"):
            try:
                docs.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue
        return docs

    def load(self, doc_id: str) -> Optional[dict]:
        path = self._path_for_id(doc_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
