"""Headless Jupyter notebook runner.

OCR engines live in ``notebooks/*.ipynb`` and are the source of truth
for the OCR logic. This module executes a notebook with ``nbclient``
and pulls a named variable out of its namespace so the rest of the
codebase can call it like a normal Python function.

The runner is deliberately generic: any service can drop a notebook
into ``notebooks/`` and expose it through this loader.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import nbformat

from app.core.logging import get_logger

logger = get_logger(__name__)


class NotebookExecutionError(RuntimeError):
    """Raised when a notebook fails to execute cleanly."""


class NotebookRunner:
    """Execute a notebook and retrieve a named variable from its namespace.

    The runner caches the most recent namespace per notebook path so a
    second call is essentially free. A forced re-run can be requested
    with ``fresh=True``.
    """

    def __init__(self, timeout: int = 600) -> None:
        self._timeout = timeout
        self._cache: dict[str, dict[str, Any]] = {}

    # --- Public API ------------------------------------------------------

    def run(
        self,
        notebook_path: str | Path,
        *,
        parameters: Mapping[str, Any] | None = None,
        fresh: bool = False,
    ) -> dict[str, Any]:
        """Execute the notebook and return its final namespace.

        ``parameters`` are exposed to the notebook cells as the variable
        ``parameters`` (a dict). They can also be set as top-level
        variables by passing ``key=value`` semantics by writing
        ``parameters["key"]`` from a cell.
        """
        path = Path(notebook_path).expanduser().resolve()
        cache_key = str(path)
        if not fresh and cache_key in self._cache:
            ns = dict(self._cache[cache_key])
            if parameters:
                ns["parameters"] = dict(parameters)
            return ns

        if not path.exists():
            raise NotebookExecutionError(f"Notebook not found: {path}")

        logger.info("running notebook path=%s", path)
        start = time.perf_counter()
        nb = nbformat.read(str(path), as_version=4)

        ns = {"parameters": dict(parameters) if parameters else {}}

        try:
            for cell in nb.cells:
                if cell.cell_type == "code":
                    exec(cell.source, ns)
        except Exception as exc:
            raise NotebookExecutionError(
                f"Cell failed in notebook {path.name}: {exc}"
            ) from exc

        elapsed = (time.perf_counter() - start) * 1000.0
        logger.info("notebook finished path=%s elapsed_ms=%.1f", path.name, elapsed)

        self._cache[cache_key] = ns
        return ns

    def get(self, notebook_path: str | Path, name: str, *, fresh: bool = False) -> Any:
        """Execute the notebook (cached) and return the named variable."""
        ns = self.run(notebook_path, fresh=fresh)
        if name not in ns:
            raise NotebookExecutionError(
                f"Notebook {Path(notebook_path).name} did not define '{name}'."
            )
        return ns[name]

    def clear_cache(self) -> None:
        """Drop the in-memory namespace cache (useful in tests)."""
        self._cache.clear()


def default_kernel_python() -> str:
    """Return the Python executable the notebook kernel will use.

    On Windows the notebook kernel is launched via ``jupyter`` which
    reads its own interpreter from the active env. We log it for
    diagnostics.
    """
    return sys.executable
