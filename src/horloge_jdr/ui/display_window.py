"""Fenêtre d'affichage (heure / compte à rebours + jour)."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from typing import TYPE_CHECKING

from .._compat import AppState
from ..controller import HorlogeController
from ..version import __version__ as APP_VERSION
from .layout import DISPLAY_LAYOUT_PARAMS, MATRIX_GREEN, apply_clock_layout
from .neon import NeonFlickerEffect

if TYPE_CHECKING:
    from .control_window import ControlWindow


def _get_icon_path() -> str | None:
    """Localise clock_icon.ico aussi bien en mode développement que dans le .exe PyInstaller."""
    try:
        if hasattr(sys, "_MEIPASS"):
            base_dir = sys._MEIPASS  # type: ignore[attr-defined]
        else:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
            )
        candidate = os.path.join(base_dir, "assets", "clock_icon.ico")
        if os.path.exists(candidate):
            return candidate
    except Exception:
        pass
    return None


class DisplayWindow(tk.Toplevel):
    """Fenêtre d'affichage (heure / compte à rebours + jour)."""

    def __init__(
        self,
        master: tk.Tk,
        controller: HorlogeController,
        control_window: ControlWindow | None = None,
    ) -> None:
        super().__init__(master)
        self.controller = controller
        self._control_window = control_window

        self.title(f"Affichage - Horloge JDR v{APP_VERSION}")
        self.configure(bg="black")
        self.minsize(300, 150)

        icon_path = _get_icon_path()
        if icon_path is not None:
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.main_frame = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        help_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        help_frame.pack(fill=tk.X, padx=10, pady=(10, 4))

        self.help_label = tk.Label(
            help_frame,
            text="Ctrl + C : rouvrir la fenêtre de contrôle",
            fg="red",
            bg="black",
            anchor="w",
            font=("Courier New", 10, "bold"),
        )
        self.help_label.pack(side=tk.LEFT, anchor="w")

        self.display_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        initial_state = controller.state if isinstance(controller.state, AppState) else None
        initial_time = initial_state.current_display_text() if initial_state else "00:00"
        initial_day = initial_state.current_day_text() if initial_state else "Jour 0"
        initial_message = (initial_state.display_message if initial_state else "") or ""
        initial_message_right = (initial_state.display_message_right if initial_state else "") or ""

        self.time_label = tk.Label(
            self.display_frame,
            text=initial_time,
            fg="red",
            bg="black",
            anchor="center",
        )

        self.day_label = tk.Label(
            self.display_frame,
            text=initial_day,
            fg="red",
            bg="black",
            anchor="ne",
        )

        self.message_label = tk.Label(
            self.display_frame,
            text=initial_message,
            fg=MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self.message_right_label = tk.Label(
            self.display_frame,
            text=initial_message_right,
            fg=MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._message_left_visible = bool(initial_message.strip())
        self._message_right_visible = bool(initial_message_right.strip())

        self._layout_busy = False
        self._last_message_fit_key: tuple[object, ...] | None = None
        self._display_config_wh = (0, 0)

        self._time_flicker = NeonFlickerEffect(self, self.time_label, prob=0.04)
        self._day_flicker = NeonFlickerEffect(self, self.day_label, prob=0.10)

        self.display_frame.bind("<Configure>", self._on_display_configure)
        self.bind_all("<Control-c>", self._on_show_control_window)

        self.controller.add_listener(self._on_state_changed)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._update_fonts()
        self._update_help_visibility()
        self._schedule_help_visibility_check()

    def _on_state_changed(self, state: AppState) -> None:
        if not self.winfo_exists():
            try:
                self.controller.remove_listener(self._on_state_changed)
            except Exception:
                pass
            return
        try:
            self.time_label.config(text=state.current_display_text())
            self.day_label.config(text=state.current_day_text())
            self._sync_display_messages(state.display_message, state.display_message_right)
        except tk.TclError:
            try:
                self.controller.remove_listener(self._on_state_changed)
            except Exception:
                pass
            return
        self.after_idle(self._update_fonts)

    def _sync_display_messages(self, text_left: str, text_right: str) -> None:
        self._message_left_visible = bool(text_left.strip())
        self._message_right_visible = bool(text_right.strip())
        self.message_label.config(text=text_left)
        self.message_right_label.config(text=text_right)

    def _on_display_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        if event.widget != self.display_frame:
            return
        w, h = int(event.width), int(event.height)
        if w < 2 or h < 2:
            return
        if (w, h) == self._display_config_wh:
            return
        self._display_config_wh = (w, h)
        self._last_message_fit_key = None
        self.after_idle(self._update_fonts)

    def _update_fonts(self) -> None:
        if self._layout_busy:
            return
        self._layout_busy = True
        try:
            self._last_message_fit_key = apply_clock_layout(
                self,
                self.display_frame,
                self.time_label,
                self.day_label,
                self.message_label,
                self.message_right_label,
                message_left_visible=self._message_left_visible,
                message_right_visible=self._message_right_visible,
                last_fit_key=self._last_message_fit_key,
                params=DISPLAY_LAYOUT_PARAMS,
            )
        finally:
            self._layout_busy = False

    def _on_show_control_window(self, event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self._control_window is not None:
            try:
                self._control_window.deiconify()
                self._control_window.lift()
                self._control_window.focus_force()
                self._update_help_visibility()
            except tk.TclError:
                pass

    def _update_help_visibility(self) -> None:
        visible = False
        if self._control_window is not None:
            try:
                visible = bool(self._control_window.winfo_viewable())
            except tk.TclError:
                visible = False
        if visible:
            self.help_label.config(text="")
        else:
            self.help_label.config(text="Ctrl + C : rouvrir la fenêtre de contrôle")

    def _schedule_help_visibility_check(self) -> None:
        self._update_help_visibility()
        self.after(500, self._schedule_help_visibility_check)

    def _on_close(self) -> None:
        self._time_flicker.stop()
        self._day_flicker.stop()
        try:
            self.controller.remove_listener(self._on_state_changed)
        except Exception:
            pass
        self.destroy()
