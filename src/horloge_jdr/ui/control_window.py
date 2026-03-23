"""Fenêtre de contrôle (heure, jour, compte à rebours, mode d'affichage)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .._compat import AppState
from ..controller import HorlogeController
from ..version import __version__ as APP_VERSION
from .layout import (
    MATRIX_EDITOR_BG,
    MATRIX_EDITOR_BORDER,
    MATRIX_GREEN,
    MATRIX_SELECT_BG,
    PREVIEW_LAYOUT_PARAMS,
    apply_clock_layout,
)


class ControlWindow(tk.Toplevel):
    """Fenêtre de contrôle (heure, jour, compte à rebours, mode d'affichage)."""

    def __init__(self, master: tk.Tk, controller: HorlogeController) -> None:
        super().__init__(master)
        self._root = master
        self.controller = controller

        self.title(f"Contrôle - Horloge JDR v{APP_VERSION}")
        self.configure(bg="black")
        self.minsize(600, 600)

        self.main_frame = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        initial_state = controller.state if isinstance(controller.state, AppState) else None
        initial_time = initial_state.current_display_text() if initial_state else "00:00"
        initial_day = initial_state.current_day_text() if initial_state else "Jour 0"
        initial_message = (initial_state.display_message if initial_state else "") or ""
        initial_message_right = (initial_state.display_message_right if initial_state else "") or ""

        preview_frame = tk.LabelFrame(
            self.main_frame,
            text="Aperçu (écran affichage)",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self._preview_canvas = tk.Frame(
            preview_frame,
            bg="black",
            bd=0,
            highlightthickness=1,
            highlightbackground="#660000",
            height=160,
        )
        self._preview_canvas.pack(fill=tk.X, padx=6, pady=6)
        self._preview_canvas.pack_propagate(False)

        self._preview_time_label = tk.Label(
            self._preview_canvas,
            text=initial_time,
            fg="red",
            bg="black",
            anchor="center",
        )

        self._preview_day_label = tk.Label(
            self._preview_canvas,
            text=initial_day,
            fg="red",
            bg="black",
            anchor="ne",
        )

        self._preview_message_label = tk.Label(
            self._preview_canvas,
            text=initial_message,
            fg=MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._preview_message_right_label = tk.Label(
            self._preview_canvas,
            text=initial_message_right,
            fg=MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._preview_message_left_visible = bool(initial_message.strip())
        self._preview_message_right_visible = bool(initial_message_right.strip())

        self._preview_layout_busy = False
        self._last_preview_fit_key: tuple[object, ...] | None = None
        self._preview_config_wh = (0, 0)

        self._preview_canvas.bind("<Configure>", self._on_preview_canvas_configure)
        self.after_idle(self._update_preview_fonts)

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Dark.TButton",
            foreground="white",
            background="#222222",
            padding=6,
        )

        buttons_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        self._add_button(buttons_frame, "+1 h", self.controller.on_plus_hour)
        self._add_button(buttons_frame, "-1 h", self.controller.on_minus_hour)
        self._add_button(buttons_frame, "+10 min", self.controller.on_plus_10min)
        self._add_button(buttons_frame, "-10 min", self.controller.on_minus_10min)
        self._add_button(buttons_frame, "+1 j", self.controller.on_plus_day)
        self._add_button(buttons_frame, "-1 j", self.controller.on_minus_day)

        message_frame = tk.LabelFrame(
            self.main_frame,
            text="Textes sous l'horloge (gauche ~80 % / droite ~20 %)",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        message_frame.pack(fill=tk.X, pady=(0, 10))
        message_frame.grid_columnconfigure(0, weight=8)
        message_frame.grid_columnconfigure(1, weight=2)
        message_frame.grid_rowconfigure(0, weight=1)

        self._message_editor_left_wrap = tk.Frame(
            message_frame,
            bg=MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._message_editor_left_wrap.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=(6, 4))

        self._message_editor_left = tk.Text(
            self._message_editor_left_wrap,
            height=4,
            wrap="word",
            fg=MATRIX_GREEN,
            bg=MATRIX_EDITOR_BG,
            insertbackground=MATRIX_GREEN,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=6,
            pady=4,
            selectbackground=MATRIX_SELECT_BG,
            selectforeground=MATRIX_GREEN,
        )
        self._message_editor_left.pack(fill=tk.BOTH, expand=True)

        self._message_editor_right_wrap = tk.Frame(
            message_frame,
            bg=MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._message_editor_right_wrap.grid(row=0, column=1, sticky="nsew", padx=(3, 6), pady=(6, 4))

        self._message_editor_right = tk.Text(
            self._message_editor_right_wrap,
            height=4,
            width=22,
            wrap="word",
            fg=MATRIX_GREEN,
            bg=MATRIX_EDITOR_BG,
            insertbackground=MATRIX_GREEN,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=6,
            pady=4,
            selectbackground=MATRIX_SELECT_BG,
            selectforeground=MATRIX_GREEN,
        )
        self._message_editor_right.pack(fill=tk.BOTH, expand=True)

        if initial_message:
            self._message_editor_left.insert("1.0", initial_message)
        if initial_message_right:
            self._message_editor_right.insert("1.0", initial_message_right)

        apply_msg_btn = ttk.Button(
            message_frame,
            text="Appliquer les textes sur l'écran",
            style="Dark.TButton",
            command=self._on_apply_display_message,
        )
        apply_msg_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(4, 6))

        countdown_frame = tk.LabelFrame(
            self.main_frame,
            text="Compte à rebours",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        countdown_frame.pack(fill=tk.X, pady=(0, 10))

        self.countdown_minutes_var = tk.StringVar(value="5")

        minutes_label = tk.Label(countdown_frame, text="Minutes :", fg="white", bg="black")
        minutes_label.pack(side=tk.LEFT, padx=(5, 2), pady=5)

        self.minutes_entry = tk.Spinbox(
            countdown_frame,
            from_=1,
            to=999,
            textvariable=self.countdown_minutes_var,
            width=5,
        )
        self.minutes_entry.pack(side=tk.LEFT, padx=2, pady=5)

        start_btn = ttk.Button(
            countdown_frame,
            text="Démarrer",
            style="Dark.TButton",
            command=self._on_start_countdown,
        )
        start_btn.pack(side=tk.LEFT, padx=4, pady=5)

        stop_btn = ttk.Button(
            countdown_frame,
            text="Arrêter",
            style="Dark.TButton",
            command=self.controller.on_stop_countdown,
        )
        stop_btn.pack(side=tk.LEFT, padx=4, pady=5)

        reset_btn = ttk.Button(
            countdown_frame,
            text="Réinitialiser",
            style="Dark.TButton",
            command=self.controller.on_reset_countdown,
        )
        reset_btn.pack(side=tk.LEFT, padx=4, pady=5)

        mode_frame = tk.LabelFrame(
            self.main_frame,
            text="Mode d'affichage",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.display_mode_var = tk.StringVar(value="time")

        time_radio = tk.Radiobutton(
            mode_frame,
            text="Heure manuelle",
            variable=self.display_mode_var,
            value="time",
            command=self._on_display_mode_changed,
            fg="white",
            bg="black",
            selectcolor="#222222",
        )
        time_radio.pack(side=tk.LEFT, padx=5, pady=5)

        countdown_radio = tk.Radiobutton(
            mode_frame,
            text="Compte à rebours",
            variable=self.display_mode_var,
            value="countdown",
            command=self._on_display_mode_changed,
            fg="white",
            bg="black",
            selectcolor="#222222",
        )
        countdown_radio.pack(side=tk.LEFT, padx=5, pady=5)

        quit_btn = ttk.Button(
            self.main_frame,
            text="Fermer l'application",
            style="Dark.TButton",
            command=self._on_quit_app,
        )
        quit_btn.pack(fill=tk.X, pady=(0, 5))

        self.controller.add_listener(self._on_state_changed)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _add_button(self, parent: tk.Misc, text: str, command) -> None:
        btn = ttk.Button(parent, text=text, style="Dark.TButton", command=command)
        btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def _on_start_countdown(self) -> None:
        try:
            minutes = int(self.countdown_minutes_var.get())
        except ValueError:
            minutes = 0
        self.controller.on_start_countdown(minutes)

    def _on_display_mode_changed(self) -> None:
        value = self.display_mode_var.get()
        if value == "countdown":
            self.controller.on_set_display_countdown()
        else:
            self.controller.on_set_display_manual_time()

    def _on_apply_display_message(self) -> None:
        left = self._message_editor_left.get("1.0", "end-1c")
        right = self._message_editor_right.get("1.0", "end-1c")
        self.controller.on_set_display_message(left)
        self.controller.on_set_display_message_right(right)

    def _on_preview_canvas_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        if event.widget != self._preview_canvas:
            return
        w, h = int(event.width), int(event.height)
        if w < 2 or h < 2:
            return
        if (w, h) == self._preview_config_wh:
            return
        self._preview_config_wh = (w, h)
        self._last_preview_fit_key = None
        self.after_idle(self._update_preview_fonts)

    def _update_preview_fonts(self) -> None:
        if self._preview_layout_busy:
            return
        self._preview_layout_busy = True
        try:
            self._last_preview_fit_key = apply_clock_layout(
                self,
                self._preview_canvas,
                self._preview_time_label,
                self._preview_day_label,
                self._preview_message_label,
                self._preview_message_right_label,
                message_left_visible=self._preview_message_left_visible,
                message_right_visible=self._preview_message_right_visible,
                last_fit_key=self._last_preview_fit_key,
                params=PREVIEW_LAYOUT_PARAMS,
            )
        except tk.TclError:
            pass
        finally:
            self._preview_layout_busy = False

    def _on_state_changed(self, state: AppState) -> None:
        if state.display_mode.name.lower().startswith("countdown"):
            self.display_mode_var.set("countdown")
        else:
            self.display_mode_var.set("time")
        try:
            self._preview_time_label.config(text=state.current_display_text())
            self._preview_day_label.config(text=state.current_day_text())
            self._preview_message_label.config(text=state.display_message)
            self._preview_message_right_label.config(text=state.display_message_right)
            self._preview_message_left_visible = bool(state.display_message.strip())
            self._preview_message_right_visible = bool(state.display_message_right.strip())
            self.after_idle(self._update_preview_fonts)
        except tk.TclError:
            pass

    def _on_close(self) -> None:
        self.withdraw()

    def _on_quit_app(self) -> None:
        try:
            self.controller.remove_listener(self._on_state_changed)
        except Exception:
            pass
        try:
            self._root.destroy()
        except Exception:
            pass
