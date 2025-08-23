from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import networkx as nx
from pyvis.network import Network


def build_graph_from_docs(docs: List[dict], source_field: str, target_field: str) -> nx.DiGraph:
    graph = nx.DiGraph()
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        source = doc.get(source_field)
        target = doc.get(target_field)
        if source is None or target is None:
            continue
        graph.add_node(source, label=str(source))
        graph.add_node(target, label=str(target))
        graph.add_edge(source, target)
    return graph


def visualize_graph(graph: nx.DiGraph, output_html: Path, notebook: bool = False) -> Path:
    net = Network(height="600px", width="100%", directed=True, notebook=notebook)
    net.from_nx(graph)
    # Avoid notebook auto-detection which can fail in some environments.
    net.write_html(str(output_html), open_browser=False, notebook=False)
    return output_html
