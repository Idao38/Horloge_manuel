"""Placement de la fenêtre d'affichage sur multi-écrans."""

from __future__ import annotations

import tkinter as tk


def position_display_window_on_secondary_monitor(root: tk.Tk, window: tk.Toplevel) -> None:
    """Essaie de placer la fenêtre d'affichage sur un 2ème écran si disponible."""
    try:
        from screeninfo import get_monitors  # type: ignore[import-not-found]

        monitors = get_monitors()
        if len(monitors) >= 2:
            second = monitors[1]
            geometry = f"{second.width}x{second.height}+{second.x}+{second.y}"
            window.geometry(geometry)
            window.attributes("-fullscreen", True)
            return
    except Exception:
        pass

    # Fallback : fenêtre maximisée mais redimensionnable sur l'écran principal
    try:
        window.attributes("-fullscreen", False)
    except Exception:
        pass
    window.state("zoomed")
