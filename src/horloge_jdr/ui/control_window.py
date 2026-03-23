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
    matrix_font,
)
from .theme import (
    BACKGROUND,
    BTN_BG,
    LABEL_FG,
    PREVIEW_BORDER,
    RADIO_SELECT,
    SEGMENT_ACTIVE_BG,
    SEGMENT_INACTIVE_BG,
    SPINBOX_BG,
    SPINBOX_FG,
    SPINBOX_INSERT,
)


class ControlWindow(tk.Toplevel):
    """Fenêtre de contrôle (heure, jour, compte à rebours, mode d'affichage)."""

    def __init__(self, master: tk.Tk, controller: HorlogeController) -> None:
        super().__init__(master)
        self._root = master
        self.controller = controller

        self.title(f"Contrôle - Horloge JDR v{APP_VERSION}")
        self.configure(bg=BACKGROUND)
        self.minsize(600, 620)

        self.main_frame = tk.Frame(self, bg=BACKGROUND, bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        initial_state = controller.state if isinstance(controller.state, AppState) else None
        initial_time = initial_state.current_display_text() if initial_state else "00:00"
        initial_day = initial_state.current_day_text() if initial_state else "Jour 0"
        initial_message = (initial_state.display_message if initial_state else "") or ""
        initial_message_right = (initial_state.display_message_right if initial_state else "") or ""

        preview_frame = tk.LabelFrame(
            self.main_frame,
            text=" Aperçu (écran affichage) ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self._preview_canvas = tk.Frame(
            preview_frame,
            bg=BACKGROUND,
            bd=0,
            highlightthickness=2,
            highlightbackground=PREVIEW_BORDER,
            height=180,
        )
        self._preview_canvas.pack(fill=tk.X, padx=6, pady=6)
        self._preview_canvas.pack_propagate(False)

        self._preview_time_label = tk.Label(
            self._preview_canvas,
            text=initial_time,
            fg="red",
            bg=BACKGROUND,
            anchor="center",
        )

        self._preview_day_label = tk.Label(
            self._preview_canvas,
            text=initial_day,
            fg="red",
            bg=BACKGROUND,
            anchor="ne",
        )

        self._preview_message_label = tk.Label(
            self._preview_canvas,
            text=initial_message,
            fg=MATRIX_GREEN,
            bg=BACKGROUND,
            anchor="nw",
            justify="left",
        )

        self._preview_message_right_label = tk.Label(
            self._preview_canvas,
            text=initial_message_right,
            fg=MATRIX_GREEN,
            bg=BACKGROUND,
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
            foreground=LABEL_FG,
            background=BTN_BG,
            padding=(12, 8),
        )
        style.map("Dark.TButton", background=[("active", "#444444")])

        # Groupe Temps (h/min)
        time_frame = tk.LabelFrame(
            self.main_frame,
            text=" Temps ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        time_frame.pack(fill=tk.X, pady=(0, 6))
        time_buttons = tk.Frame(time_frame, bg=BACKGROUND, bd=0, highlightthickness=0)
        time_buttons.pack(fill=tk.X, padx=6, pady=(2, 6))
        self._add_button(time_buttons, "-1 h", self.controller.on_minus_hour)
        self._add_button(time_buttons, "+1 h", self.controller.on_plus_hour)
        self._add_button(time_buttons, "-10 min", self.controller.on_minus_10min)
        self._add_button(time_buttons, "+10 min", self.controller.on_plus_10min)

        # Groupe Jours
        day_frame = tk.LabelFrame(
            self.main_frame,
            text=" Jours ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        day_frame.pack(fill=tk.X, pady=(0, 10))
        day_buttons = tk.Frame(day_frame, bg=BACKGROUND, bd=0, highlightthickness=0)
        day_buttons.pack(fill=tk.X, padx=6, pady=(2, 6))
        self._add_button(day_buttons, "-1 j", self.controller.on_minus_day)
        self._add_button(day_buttons, "+1 j", self.controller.on_plus_day)

        message_frame = tk.LabelFrame(
            self.main_frame,
            text=" Textes sous l'horloge (glisser le séparateur pour ajuster) ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        message_frame.pack(fill=tk.X, pady=(0, 10))
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(0, weight=1)

        initial_ratio = initial_state.text_column_ratio if initial_state else 0.8
        weight_left = max(1, int(initial_ratio * 10))
        weight_right = max(1, 10 - weight_left)

        self._text_paned = ttk.PanedWindow(message_frame, orient=tk.HORIZONTAL)
        self._text_paned.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 4))

        self._pane_left = tk.Frame(
            self._text_paned,
            bg=MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._text_paned.add(self._pane_left, weight=weight_left)

        self._message_editor_left = tk.Text(
            self._pane_left,
            height=4,
            wrap="word",
            fg=MATRIX_GREEN,
            bg=MATRIX_EDITOR_BG,
            insertbackground=MATRIX_GREEN,
            font=matrix_font(10),
            relief=tk.FLAT,
            padx=6,
            pady=4,
            selectbackground=MATRIX_SELECT_BG,
            selectforeground=MATRIX_GREEN,
        )
        self._message_editor_left.pack(fill=tk.BOTH, expand=True)

        self._pane_right = tk.Frame(
            self._text_paned,
            bg=MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._text_paned.add(self._pane_right, weight=weight_right)

        self._message_editor_right = tk.Text(
            self._pane_right,
            height=4,
            width=12,
            wrap="word",
            fg=MATRIX_GREEN,
            bg=MATRIX_EDITOR_BG,
            insertbackground=MATRIX_GREEN,
            font=matrix_font(10),
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

        self._paned_ratio_debounce: str | None = None
        self._pane_left.bind("<Configure>", self._on_text_paned_configure)
        self._pane_right.bind("<Configure>", self._on_text_paned_configure)

        apply_msg_btn = ttk.Button(
            message_frame,
            text="Appliquer les textes sur l'écran",
            style="Dark.TButton",
            command=self._on_apply_display_message,
        )
        apply_msg_btn.grid(row=1, column=0, sticky="ew", padx=6, pady=(4, 6))

        countdown_frame = tk.LabelFrame(
            self.main_frame,
            text=" Compte à rebours ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        countdown_frame.pack(fill=tk.X, pady=(0, 10))

        self.countdown_minutes_var = tk.StringVar(value="5")

        minutes_label = tk.Label(countdown_frame, text="Minutes :", fg=LABEL_FG, bg=BACKGROUND)
        minutes_label.pack(side=tk.LEFT, padx=(5, 2), pady=5)

        self.minutes_entry = tk.Spinbox(
            countdown_frame,
            from_=1,
            to=999,
            textvariable=self.countdown_minutes_var,
            width=5,
            bg=SPINBOX_BG,
            fg=SPINBOX_FG,
            insertbackground=SPINBOX_INSERT,
            highlightthickness=1,
            highlightbackground=MATRIX_EDITOR_BORDER,
            buttonbackground=BTN_BG,
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
            text=" Mode d'affichage ",
            fg=LABEL_FG,
            bg=BACKGROUND,
            bd=1,
            highlightthickness=0,
        )
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.display_mode_var = tk.StringVar(value="time")
        segment_frame = tk.Frame(mode_frame, bg=BACKGROUND, bd=0, highlightthickness=0)
        segment_frame.pack(fill=tk.X, padx=6, pady=(2, 6))

        self._btn_time = tk.Button(
            segment_frame,
            text="Heure",
            fg=LABEL_FG,
            bg=SEGMENT_ACTIVE_BG,
            activebackground=SEGMENT_ACTIVE_BG,
            activeforeground=LABEL_FG,
            relief=tk.SUNKEN,
            bd=1,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_mode_time,
        )
        self._btn_time.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 1))

        self._btn_countdown = tk.Button(
            segment_frame,
            text="Compte à rebours",
            fg=LABEL_FG,
            bg=SEGMENT_INACTIVE_BG,
            activebackground=SEGMENT_ACTIVE_BG,
            activeforeground=LABEL_FG,
            relief=tk.RAISED,
            bd=1,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_mode_countdown,
        )
        self._btn_countdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(1, 0))

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

    def _on_mode_time(self) -> None:
        self.display_mode_var.set("time")
        self.controller.on_set_display_manual_time()
        self._update_mode_segment_visual()

    def _on_mode_countdown(self) -> None:
        self.display_mode_var.set("countdown")
        self.controller.on_set_display_countdown()
        self._update_mode_segment_visual()

    def _update_mode_segment_visual(self) -> None:
        """Met à jour l'apparence du segmented control selon le mode actif."""
        is_time = self.display_mode_var.get() == "time"
        self._btn_time.config(
            bg=SEGMENT_ACTIVE_BG if is_time else SEGMENT_INACTIVE_BG,
            relief=tk.SUNKEN if is_time else tk.RAISED,
        )
        self._btn_countdown.config(
            bg=SEGMENT_ACTIVE_BG if not is_time else SEGMENT_INACTIVE_BG,
            relief=tk.SUNKEN if not is_time else tk.RAISED,
        )

    def _on_apply_display_message(self) -> None:
        left = self._message_editor_left.get("1.0", "end-1c")
        right = self._message_editor_right.get("1.0", "end-1c")
        self.controller.on_set_display_message(left)
        self.controller.on_set_display_message_right(right)

    def _on_text_paned_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Détecte le redimensionnement des panneaux (glissement du séparateur) et met à jour le ratio."""
        if self._paned_ratio_debounce is not None:
            self.after_cancel(self._paned_ratio_debounce)
        self._paned_ratio_debounce = self.after(100, self._update_ratio_from_paned)

    def _update_ratio_from_paned(self) -> None:
        self._paned_ratio_debounce = None
        try:
            w_left = self._pane_left.winfo_width()
            w_total = self._text_paned.winfo_width()
            if w_total < 10:
                return
            ratio = w_left / float(w_total)
            self.controller.on_set_text_column_ratio(ratio)
        except (tk.TclError, ZeroDivisionError):
            pass

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
            state = self.controller.state
            ratio = state.text_column_ratio if isinstance(state, AppState) else None
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
                left_column_ratio=ratio,
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
        self._update_mode_segment_visual()
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
