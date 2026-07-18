"""dots: JSON storage, JSONiq/JMESPath queries, and directed graph analysis.

Re-exports the public library API so downstream packages can simply do::

    from dots import JsonStorage, run_jmespath, build_graph_from_docs
"""
from __future__ import annotations

from .graph import build_graph_from_docs, visualize_graph
from .query import run_jmespath, run_jsoniq
from .storage import JsonStorage

__version__ = "0.1.0"

__all__ = [
    "JsonStorage",
    "run_jmespath",
    "run_jsoniq",
    "build_graph_from_docs",
    "visualize_graph",
    "__version__",
]
