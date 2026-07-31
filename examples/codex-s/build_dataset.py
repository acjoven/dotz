#!/usr/bin/env python3
"""Build a `dotz`-compatible knowledge graph example from the CoDEx-S dataset.

CoDEx (https://github.com/tsafavi/codex) is a set of knowledge graph completion
datasets extracted from Wikidata and Wikipedia, released under the MIT license.
CoDEx-S is the smallest variant (2,034 entities, 42 relations, 36,543 triples)
and is a compact-but-realistic knowledge graph for testing tooling at scale.

This script downloads the raw CoDEx-S triple/label files and converts them into
two JSON files in the `dotz` node/edge document format:

* ``codex_s_dotz.json``   -- the full graph, using canonical Wikidata IDs
  (``Q...`` entities, ``P...`` relations) as document ids for stability.
* ``codex_s_sample.json`` -- a small, human-readable ego-network subgraph that
  uses entity *labels* as ids so ``dotz graph build`` renders a readable graph.

Usage::

    python examples/codex-s/build_dataset.py            # download + build
    python examples/codex-s/build_dataset.py --source-dir /path/to/raw

Raw files expected (auto-downloaded when missing):
    triples/codex-s/{train,valid,test}.txt
    entities/en/entities.json
    relations/en/relations.json
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

RAW_BASE = "https://raw.githubusercontent.com/tsafavi/codex/master/data"
REMOTE_FILES = {
    "train.txt": f"{RAW_BASE}/triples/codex-s/train.txt",
    "valid.txt": f"{RAW_BASE}/triples/codex-s/valid.txt",
    "test.txt": f"{RAW_BASE}/triples/codex-s/test.txt",
    "entities.json": f"{RAW_BASE}/entities/en/entities.json",
    "relations.json": f"{RAW_BASE}/relations/en/relations.json",
}

# Seed entity for the readable sample subgraph (Wikidata QID). Q84 = London.
SAMPLE_SEED = "Q84"
SAMPLE_MAX_EDGES = 150


def _ensure_raw(source_dir: Path) -> Path:
    source_dir.mkdir(parents=True, exist_ok=True)
    for name, url in REMOTE_FILES.items():
        dest = source_dir / name
        if not dest.exists():
            print(f"Downloading {url}")
            urllib.request.urlretrieve(url, dest)
    return source_dir


def _read_triples(source_dir: Path) -> List[Tuple[str, str, str]]:
    triples: List[Tuple[str, str, str]] = []
    for split in ("train.txt", "valid.txt", "test.txt"):
        for line in (source_dir / split).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                head, rel, tail = line.split("\t")
                triples.append((head, rel, tail))
    return triples


def build_full(triples, ents, rels) -> List[dict]:
    used = {q for h, _, t in triples for q in (h, t)}
    docs: List[dict] = []
    for qid in sorted(used):
        meta = ents.get(qid, {})
        docs.append(
            {
                "id": qid,
                "type": "node",
                "label": meta.get("label", qid),
                "description": meta.get("description"),
                "wiki": meta.get("wiki"),
            }
        )
    for head, rel, tail in triples:
        docs.append(
            {
                "type": "edge",
                "source": head,
                "target": tail,
                "relation": rels.get(rel, {}).get("label", rel),
                "pid": rel,
            }
        )
    return docs


def build_sample(triples, ents, rels, seed: str, max_edges: int) -> List[dict]:
    """One-hop ego network around ``seed`` using labels as ids (readable graph)."""
    def label(qid: str) -> str:
        return ents.get(qid, {}).get("label", qid)

    ego = [(h, r, t) for h, r, t in triples if h == seed or t == seed][:max_edges]
    nodes: Dict[str, dict] = {}
    edges: List[dict] = []
    for head, rel, tail in ego:
        for qid in (head, tail):
            lab = label(qid)
            if lab not in nodes:
                meta = ents.get(qid, {})
                nodes[lab] = {
                    "id": lab,
                    "type": "node",
                    "label": lab,
                    "qid": qid,
                    "description": meta.get("description"),
                }
        edges.append(
            {
                "type": "edge",
                "source": label(head),
                "target": label(tail),
                "relation": rels.get(rel, {}).get("label", rel),
                "pid": rel,
            }
        )
    return list(nodes.values()) + edges


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=here / "_raw",
                        help="Directory holding (or to download) the raw CoDEx-S files")
    parser.add_argument("--out-dir", type=Path, default=here, help="Output directory")
    args = parser.parse_args()

    source_dir = _ensure_raw(args.source_dir)
    ents = json.loads((source_dir / "entities.json").read_text(encoding="utf-8"))
    rels = json.loads((source_dir / "relations.json").read_text(encoding="utf-8"))
    triples = _read_triples(source_dir)

    full = build_full(triples, ents, rels)
    sample = build_sample(triples, ents, rels, SAMPLE_SEED, SAMPLE_MAX_EDGES)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    full_path = args.out_dir / "codex_s_dotz.json"
    sample_path = args.out_dir / "codex_s_sample.json"
    full_path.write_text(json.dumps(full, ensure_ascii=False, indent=1), encoding="utf-8")
    sample_path.write_text(json.dumps(sample, ensure_ascii=False, indent=1), encoding="utf-8")

    n_nodes = sum(1 for d in full if d["type"] == "node")
    n_edges = sum(1 for d in full if d["type"] == "edge")
    print(f"Wrote {full_path} ({n_nodes} nodes, {n_edges} edges)")
    s_nodes = sum(1 for d in sample if d["type"] == "node")
    s_edges = sum(1 for d in sample if d["type"] == "edge")
    print(f"Wrote {sample_path} ({s_nodes} nodes, {s_edges} edges)")


if __name__ == "__main__":
    main()
