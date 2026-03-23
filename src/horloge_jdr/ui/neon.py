"""Effet de clignotement type néon pour les labels Tkinter."""

from __future__ import annotations

import random
import tkinter as tk


class NeonFlickerEffect:
    """Effet de clignotement type néon pour un label Tkinter."""

    def __init__(self, root: tk.Misc, widget: tk.Label, prob: float) -> None:
        self._root = root
        self._widget = widget
        self._prob = prob
        self._running = True
        self._schedule_tick()

    def stop(self) -> None:
        self._running = False

    def _schedule_tick(self) -> None:
        if not self._running:
            return
        self._root.after(1000, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return
        if random.random() < self._prob:
            self._start_flicker()
        self._schedule_tick()

    def _start_flicker(self) -> None:
        sequence = ["#330000", "#880000", "#330000", "#FF0000"]
        self._flicker_step(sequence, 0)

    def _flicker_step(self, colors: list[str], index: int) -> None:
        if index >= len(colors):
            return
        try:
            self._widget.config(fg=colors[index])
        except tk.TclError:
            return
        self._root.after(70, lambda: self._flicker_step(colors, index + 1))
