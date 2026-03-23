"""Thème centralisé : couleurs et polices pour l'interface Horloge JDR."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont

# === Affichage principal (écran projeté) ===
BACKGROUND = "black"

# Heure et jour : néon rouge
CLOCK_FG = "red"
NEON_FLICKER_COLORS = ["#550000", "#880000", "#550000", "#FF0000"]  # #550000 au lieu de #330000

# Bandeau d'aide : teinte distincte pour ne pas concurrencer l'heure
HELP_FG = "#CC9933"  # ambre

# Zone texte Matrix : vert terminal
MATRIX_GREEN = "#00FF41"
MATRIX_EDITOR_BG = "#030803"
MATRIX_EDITOR_BORDER = "#2d6a3d"
MATRIX_SELECT_BG = "#003311"

# Aperçu (fenêtre MJ)
PREVIEW_BORDER = "#AA3333"  # bordure plus visible

# Fenêtre MJ : boutons et contrôles
BTN_FG = "white"
BTN_BG = "#333333"
SPINBOX_BG = "#1a1a1a"
SPINBOX_FG = "white"
SPINBOX_INSERT = "#00FF41"
SPINBOX_BORDER = "#444444"
RADIO_SELECT = "#333333"
LABEL_FG = "#CCCCCC"

# Segmented control (mode Heure / Compte)
SEGMENT_ACTIVE_BG = "#555555"   # segment actif (enfoncé)
SEGMENT_INACTIVE_BG = "#222222"  # segment inactif


_MATRIX_FONT_CACHE: str | None = None

_MATRIX_FONT_CANDIDATES = (
    "Lucida Console",      # Windows, zéro plus ouvert
    "DejaVu Sans Mono",    # zéro barré si installé
    "Liberation Mono",     # zéro barré si installé
    "Consolas",            # fallback Windows
)


def get_matrix_font_family() -> str:
    """
    Police monospace pour la zone texte Matrix (meilleure distinction 0/8 à petite taille).
    Cache le résultat. Appeler après que Tk soit initialisé.
    """
    global _MATRIX_FONT_CACHE
    if _MATRIX_FONT_CACHE is not None:
        return _MATRIX_FONT_CACHE
    for family in _MATRIX_FONT_CANDIDATES:
        try:
            font = tkfont.Font(family=family, size=10)
            if font.actual()["family"] == family:
                _MATRIX_FONT_CACHE = family
                return family
        except tk.TclError:
            continue
    _MATRIX_FONT_CACHE = "Consolas"
    return "Consolas"
