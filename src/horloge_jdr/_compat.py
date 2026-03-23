"""Imports adaptés au contexte package vs exécutable PyInstaller."""

from __future__ import annotations

import sys

if getattr(sys, "frozen", False):
    # Contexte exécutable PyInstaller
    from horloge_jdr.domain import AppState  # type: ignore[import-not-found]
else:
    # Contexte package
    from .domain import AppState

__all__ = ["AppState"]
