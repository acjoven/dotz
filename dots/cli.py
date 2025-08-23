from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from .storage import JsonStorage
from .query import run_jmespath, run_jsoniq
from .graph import build_graph_from_docs, visualize_graph

app = typer.Typer(no_args_is_help=True)


@app.command()
def version():
    print("dots CLI 0.1.0")


store_app = typer.Typer(no_args_is_help=True)
query_app = typer.Typer(no_args_is_help=True)
graph_app = typer.Typer(no_args_is_help=True)

app.add_typer(store_app, name="store", help="JSON storage commands")
app.add_typer(query_app, name="query", help="Query commands (JSONiq / JMESPath)")
app.add_typer(graph_app, name="graph", help="Graph operations")


@store_app.command("ingest")
def store_ingest(
    source: Path = typer.Argument(..., exists=True, readable=True, help="JSON file (.json or .jsonl)"),
    id_field: Optional[str] = typer.Option(None, help="Field to use as document id; else UUID"),
    data_dir: Optional[Path] = typer.Option(None, help="Data directory (defaults to ./data)"),
    schema_path: Optional[Path] = typer.Option(None, "--schema", exists=True, readable=True, help="Path to JSON Schema file"),
):
    storage = JsonStorage.create(data_dir)
    schema = None
    if schema_path:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    ids = storage.ingest(source, id_field=id_field, schema=schema)
    print({"ingested": ids})


@store_app.command("list")
def store_list(
    data_dir: Optional[Path] = typer.Option(None, help="Data directory (defaults to ./data)"),
):
    storage = JsonStorage.create(data_dir)
    ids = storage.list_ids()
    print({"count": len(ids), "ids": ids})


@query_app.command("jmespath")
def query_jmespath(
    expression: str = typer.Argument(..., help="JMESPath expression"),
    data_dir: Optional[Path] = typer.Option(None, help="Data directory (defaults to ./data)"),
):
    storage = JsonStorage.create(data_dir)
    docs = storage.load_all()
    result = run_jmespath(expression, docs)
    print(json.dumps(result, ensure_ascii=False, indent=2))


@query_app.command("jsoniq")
def query_jsoniq(
    file: Optional[Path] = typer.Option(None, "--file", exists=True, readable=True, help="File containing JSONiq query"),
    expr: Optional[str] = typer.Option(None, "--expr", help="Inline JSONiq expression"),
    data_dir: Optional[Path] = typer.Option(None, help="Data directory (defaults to ./data)"),
):
    if not file and not expr:
        raise typer.BadParameter("Provide --file or --expr")
    query_text = file.read_text(encoding="utf-8") if file else str(expr)
    storage = JsonStorage.create(data_dir)
    ok, out = run_jsoniq(query_text, storage.data_dir)
    if ok:
        print(out)
    else:
        print("[yellow]JSONiq engine unavailable or failed.\nFallback: use 'dots query jmespath' instead.[/yellow]")
        print(out)


@graph_app.command("build")
def graph_build(
    source_field: str = typer.Option(..., help="Field name for source node"),
    target_field: str = typer.Option(..., help="Field name for target node"),
    output: Path = typer.Option(Path("graph.html"), help="Output HTML path"),
    data_dir: Optional[Path] = typer.Option(None, help="Data directory (defaults to ./data)"),
):
    storage = JsonStorage.create(data_dir)
    docs = storage.load_all()
    g = build_graph_from_docs(docs, source_field, target_field)
    visualize_graph(g, output)
    print({"nodes": g.number_of_nodes(), "edges": g.number_of_edges(), "output": str(output)})


if __name__ == "__main__":
    app()
