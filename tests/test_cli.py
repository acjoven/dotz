from pathlib import Path
import json
import subprocess
import sys


def run_cli(args):
    return subprocess.run([sys.executable, "-m", "dots.cli", *args], capture_output=True, text=True, check=False)


def test_store_and_list(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DOTS_DATA_DIR", str(tmp_path / "data"))
    data = [
        {"id": "X", "type": "node"},
        {"id": "Y", "type": "node"},
        {"type": "edge", "source": "X", "target": "Y"},
    ]
    src = tmp_path / "input.json"
    src.write_text(json.dumps(data), encoding="utf-8")

    r = run_cli(["store", "ingest", str(src), "--id-field", "id"]) 
    assert r.returncode == 0

    r = run_cli(["store", "list"]) 
    assert r.returncode == 0
    assert '"X"' in r.stdout and '"Y"' in r.stdout


def test_jmespath_query(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DOTS_DATA_DIR", str(tmp_path / "data"))
    data = [
        {"id": "X", "type": "node"},
        {"id": "Y", "type": "node"},
        {"type": "edge", "source": "X", "target": "Y"},
    ]
    src = tmp_path / "input.json"
    src.write_text(json.dumps(data), encoding="utf-8")
    run_cli(["store", "ingest", str(src), "--id-field", "id"]) 

    r = run_cli(["query", "jmespath", "[?type=='edge']"]) 
    assert r.returncode == 0
    assert '"edge"' in r.stdout


def test_graph_build(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DOTS_DATA_DIR", str(tmp_path / "data"))
    data = [
        {"id": "X", "type": "node"},
        {"id": "Y", "type": "node"},
        {"type": "edge", "source": "X", "target": "Y"},
    ]
    src = tmp_path / "input.json"
    src.write_text(json.dumps(data), encoding="utf-8")
    run_cli(["store", "ingest", str(src), "--id-field", "id"]) 

    out = tmp_path / "graph.html"
    r = run_cli(["graph", "build", "--source-field", "source", "--target-field", "target", "--output", str(out)])
    assert r.returncode == 0
    assert out.exists()


