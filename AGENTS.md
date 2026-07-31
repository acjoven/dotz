# AGENTS.md

## Cursor Cloud specific instructions

`dotz` is a single Python CLI toolkit (no web server / long-running service). Core
functionality lives in `dotz/` and is exercised via `python -m dotz.cli`:
storage (`store ingest` / `store list`), querying (`query jmespath`, and optional
`query jsoniq`), and directed-graph visualization (`graph build` -> HTML). See
`README.md` for the full command reference.

Dependencies are installed into a virtualenv at `.venv` (gitignored). Activate it
or call binaries directly, e.g. `.venv/bin/python -m dotz.cli --help`.

### Running / testing / lint
- Tests: `.venv/bin/python -m pytest` (suite is `tests/test_cli.py`).
- Lint: no linter is configured in this repo. For a quick syntax sanity check use
  `.venv/bin/python -m py_compile dotz/*.py scripts/*.py tests/*.py`.
- Run end-to-end (no external services needed):
  `DOTZ_DATA_DIR=/tmp/demo .venv/bin/python -m dotz.cli store ingest data/examples.json --id-field id`
  then `... graph build --source-field source --target-field target --output graph.html`.
  `graph.html` is a self-contained pyvis/vis.js page; serve it (e.g.
  `python -m http.server`) to view in a browser.

### Non-obvious gotchas
- `typer==0.12.5` is NOT compatible with `click>=8.2` (raises
  `TyperArgument.make_metavar() takes 1 positional argument but 2 were given` and
  "Got unexpected extra argument"). `requirements.txt` pins `click<8.2`; keep that
  constraint. The startup update script also reinstalls `click<8.2` defensively.
- The RumbleDB (JSONiq), Spark, and Hadoop services in `docker-compose.yml` are
  OPTIONAL and require Docker (not installed by default here). `query jmespath`,
  `store`, and `graph` all work without Docker. `query jsoniq` gracefully falls
  back with a message when Docker is unavailable.
