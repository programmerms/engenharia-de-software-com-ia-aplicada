"""Fachada de compatibilidade para a factory canônica.

O Composition Root oficial está em ``app.factory.build``.
"""

from __future__ import annotations

from app.factory.build import build_graph

__all__ = ["build_graph"]
