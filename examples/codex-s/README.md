# CoDEx-S knowledge graph example

A representative, real-world knowledge graph for exercising the `dots` toolkit at
a larger scale than the toy `data/examples.json` fixture.

## Source & license

- **Dataset:** [CoDEx](https://github.com/tsafavi/codex) (CoDEx-S variant) — a set of
  Knowledge Graph **Co**mpletion **D**atasets **Ex**tracted from Wikidata and Wikipedia.
- **Paper:** Tara Safavi and Danai Koutra, *CoDEx: A Comprehensive Knowledge Graph
  Completion Benchmark*, EMNLP 2020. <https://aclanthology.org/2020.emnlp-main.669/>
- **License:** MIT (see the upstream repository). Underlying data is derived from
  Wikidata (CC0) and Wikipedia.

## Files

| File | Docs | Description |
|------|------|-------------|
| `codex_s_dots.json` | 2,034 nodes + 36,543 edges | Full CoDEx-S graph. Uses canonical Wikidata IDs (`Q...`) as node `id` and edge `source`/`target`; entity `label`/`description`/`wiki` and relation `label`/`pid` are preserved. Use this to test tooling at scale. |
| `codex_s_sample.json` | 77 nodes + 86 edges | One-hop ego network around **London** (`Q84`). Uses human-readable entity *labels* as ids so `dots graph build` renders a readable graph out of the box. Great for quick visual demos. |
| `build_dataset.py` | — | Reproducible generator. Downloads the raw CoDEx-S files and rebuilds both JSON files. |

## Document format

Each file is a JSON array of `dots` documents:

```jsonc
// node
{"id": "Q84", "type": "node", "label": "London", "description": "...", "wiki": "..."}
// edge
{"type": "edge", "source": "Q1060636", "target": "Q62", "relation": "place of birth", "pid": "P19"}
```

## Usage

```bash
# Point the store at a scratch dir so you don't mix with ./data
export DOTS_DATA_DIR=/tmp/codex-s

# --- Readable sample (recommended for visualization) ---
python -m dots.cli store ingest examples/codex-s/codex_s_sample.json --id-field id
python -m dots.cli graph build --source-field source --target-field target --output codex_s_sample.html
# open codex_s_sample.html

# --- Full graph (scale test) ---
export DOTS_DATA_DIR=/tmp/codex-s-full
python -m dots.cli store ingest examples/codex-s/codex_s_dots.json --id-field id
python -m dots.cli store list                       # 38,577 docs
python -m dots.cli query jmespath "length([?relation=='place of birth'])"
python -m dots.cli graph build --source-field source --target-field target --output codex_s_full.html
```

> Note: `dots graph build` uses a `networkx.DiGraph`, so multiple edges between the
> same pair of nodes collapse into one; the full graph therefore renders ~36,203
> unique directed edges. Rendering all 36k edges in a browser is heavy — prefer
> `codex_s_sample.json` for interactive visualization.

## Regenerating

```bash
python examples/codex-s/build_dataset.py          # downloads raw files, rebuilds both JSONs
```
