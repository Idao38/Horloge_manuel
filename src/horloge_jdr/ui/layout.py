"""Mise en page commune pour l'horloge (fenêtre d'affichage et aperçu)."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk

# Texte libre sous l'horloge : style terminal / Matrix
MATRIX_GREEN = "#00FF41"
MATRIX_EDITOR_BG = "#030803"
MATRIX_EDITOR_BORDER = "#2d6a3d"
MATRIX_SELECT_BG = "#003311"

# Colonnes sous l'horloge : ~80 % gauche / 20 % droite (avec marges)
LEFT_TEXT_MARGIN_REL = 0.01
GAP_TEXT_COLUMNS_REL = 0.01
RIGHT_TEXT_RELWIDTH = 0.20
LEFT_TEXT_RELWIDTH_BOTH = 1.0 - LEFT_TEXT_MARGIN_REL - GAP_TEXT_COLUMNS_REL - RIGHT_TEXT_RELWIDTH

# Police Matrix : taille mini pour le rétrécissement adaptatif
MATRIX_MIN_FONT = 5


def matrix_font(size: int) -> tuple[str, int, str]:
    """Police monospace type terminal ; Consolas est généralement disponible sous Windows."""
    return ("Consolas", max(size, MATRIX_MIN_FONT), "normal")


def fit_matrix_label_to_height(
    root: tk.Misc,
    label: tk.Label,
    *,
    wraplength_px: int,
    max_height_px: float,
    max_font: int,
    min_font: int = MATRIX_MIN_FONT,
) -> int:
    """
    Plus grande taille de police pour que le Label (wraplength fixé) tienne en hauteur.
    Recherche dichotomique : peu d'appels à update_idletasks (évite boucles / plantages).
    """
    min_font = max(min_font, MATRIX_MIN_FONT)
    max_font = max(max_font, min_font)
    wl = max(1, int(wraplength_px))
    lo, hi = min_font, max_font
    best = min_font
    limit = float(max_height_px) + 4.0
    while lo <= hi:
        mid = (lo + hi) // 2
        label.config(font=matrix_font(mid), wraplength=wl, fg=MATRIX_GREEN)
        root.update_idletasks()
        try:
            h = float(label.winfo_reqheight())
        except tk.TclError:
            h = limit + 1.0
        if h <= limit:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    label.config(font=matrix_font(best), wraplength=wl, fg=MATRIX_GREEN)
    return best


@dataclass
class ClockLayoutParams:
    """Paramètres d'échelle pour le layout (Display vs Preview)."""

    min_font_size: int = 20
    gap_px: float = 12.0
    day_offset_x: int = -10
    day_offset_y: int = 10
    msg_bottom_margin: float = 16.0
    msg_min_height: float = 24.0
    wraplength_left_subtract: int = 24
    wraplength_left_min: int = 40
    wraplength_right_subtract: int = 16
    wraplength_right_min: int = 24


PREVIEW_LAYOUT_PARAMS = ClockLayoutParams(
    min_font_size=14,
    gap_px=6.0,
    day_offset_x=-8,
    day_offset_y=6,
    msg_bottom_margin=8.0,
    msg_min_height=12.0,
    wraplength_left_subtract=16,
    wraplength_left_min=24,
    wraplength_right_subtract=12,
    wraplength_right_min=16,
)

DISPLAY_LAYOUT_PARAMS = ClockLayoutParams()


def apply_clock_layout(
    root: tk.Misc,
    container: tk.Widget,
    time_label: tk.Label,
    day_label: tk.Label,
    message_label: tk.Label,
    message_right_label: tk.Label,
    *,
    message_left_visible: bool,
    message_right_visible: bool,
    last_fit_key: tuple[object, ...] | None,
    params: ClockLayoutParams = DISPLAY_LAYOUT_PARAMS,
) -> tuple[object, ...] | None:
    """
    Applique la mise en page commune (heure, jour, colonnes Matrix).
    Retourne le fit_key mis à jour pour éviter les recalculs inutiles.
    """
    root.update_idletasks()
    width = max(container.winfo_width(), 1)
    height = max(container.winfo_height(), 1)

    base = min(width // 5, height // 2)
    font_size = max(base, params.min_font_size)
    time_label.config(font=("Courier New", font_size, "bold"))
    day_label.config(font=("Courier New", max(font_size // 4, 8), "bold"))

    time_label.place(relx=0.5, rely=0.5, anchor="center")
    day_label.place(relx=1.0, rely=0.0, anchor="ne", x=params.day_offset_x, y=params.day_offset_y)

    if not (message_left_visible or message_right_visible):
        message_label.place_forget()
        message_right_label.place_forget()
        return None

    txt_l = message_label.cget("text") or ""
    txt_r = message_right_label.cget("text") or ""
    fit_key = (
        int(width),
        int(height),
        txt_l,
        txt_r,
        message_left_visible,
        message_right_visible,
    )
    if fit_key == last_fit_key:
        return last_fit_key

    root.update_idletasks()
    time_h = float(time_label.winfo_reqheight())
    msg_rely = (0.5 * float(height) + time_h / 2.0 + params.gap_px) / float(height)
    msg_rely = min(max(msg_rely, 0.02), 0.96)

    msg_top_px = msg_rely * float(height)
    msg_h = max(float(height) - msg_top_px - params.msg_bottom_margin, params.msg_min_height)
    base_msg = max(font_size // 6, 6)
    both = message_left_visible and message_right_visible

    if message_left_visible:
        wl = max(
            int(width * (LEFT_TEXT_RELWIDTH_BOTH if both else 0.98) - params.wraplength_left_subtract),
            params.wraplength_left_min,
        )
        if both:
            message_label.place(
                relx=LEFT_TEXT_MARGIN_REL,
                rely=msg_rely,
                anchor="nw",
                relwidth=LEFT_TEXT_RELWIDTH_BOTH,
            )
        else:
            message_label.place(relx=LEFT_TEXT_MARGIN_REL, rely=msg_rely, anchor="nw", relwidth=0.98)
        fit_matrix_label_to_height(
            root,
            message_label,
            wraplength_px=wl,
            max_height_px=msg_h,
            max_font=base_msg,
        )

    if message_right_visible:
        wr = max(int(width * RIGHT_TEXT_RELWIDTH - params.wraplength_right_subtract), params.wraplength_right_min)
        relx_r = (
            LEFT_TEXT_MARGIN_REL + LEFT_TEXT_RELWIDTH_BOTH + GAP_TEXT_COLUMNS_REL
            if both
            else 1.0 - RIGHT_TEXT_RELWIDTH - LEFT_TEXT_MARGIN_REL
        )
        message_right_label.place(relx=relx_r, rely=msg_rely, anchor="nw", relwidth=RIGHT_TEXT_RELWIDTH)
        fit_matrix_label_to_height(
            root,
            message_right_label,
            wraplength_px=wr,
            max_height_px=msg_h,
            max_font=base_msg,
        )

    if message_left_visible:
        time_label.lift(message_label)
        day_label.lift(message_label)
    if message_right_visible:
        time_label.lift(message_right_label)
        day_label.lift(message_right_label)
    if not message_left_visible:
        message_label.place_forget()
    if not message_right_visible:
        message_right_label.place_forget()

    return fit_key
